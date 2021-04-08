import cx_Oracle
import datetime as dt
import time

cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_19_8_2")

user = "skud_report1"
pw = "Pre49Fdm!"
dsn = "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=ora-preproduction.tpu.ru)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=STORE)))"

def calculate(id,month,year):
    myconnection = cx_Oracle.connect(user, pw, dsn)

    mycursor = myconnection.cursor()
    mycursor.execute(
        "select a.lichnost_id, a.build_id, a.direction, a.event_time from guard_add_prohod.passages a where a.lichnost_id =" + str(id))
    result = mycursor.fetchall()
    newList = []

    mycursor.execute(
        "select o.lichnost_id,o.otpusk_start_data,o.otpusk_end_date from sotrudnik.otpusk_detaly_v o where o.otpusk_start_data not like 'None' AND o.lichnost_id =" + str(id))
    result2 = mycursor.fetchall()
    newList2 = []

    # Выборка данных по месяцу
    for row in result:
        if (row[3].month == month) and (row[3].year == year):
            newList.append(row)


    for row in result2:
        if (row[1].month == month or row[2].month == month) and (row[1].year == year or row[2].year == year):
            newList2.append(row)

    # Сортировка
    sorResult = sorted(newList, key=lambda row: row[3])
    sorResult2 = sorted(newList2, key=lambda row: row[1])

    # Подсчет количества рабочих дней
    numOfDays = 0
    workDays = []
    for n in range(32):
        for sorRow in sorResult:
            if n == sorRow[3].day:
                numOfDays = numOfDays + 1
                workDays.append(n)
                n = n + 1
                break

    # Подсчет дней отпуска в месяце
    vacDays = []
    for n in range(1, 31):
        for row in sorResult2:
            day = dt.datetime(year, month, n, 12)
            if day <= row[2] and day >= row[1]:
                vacDays.append(n)

    # Количество раз выхода на работу в отпуске
    workVacDays = 0
    for v in vacDays:
        for w in workDays:
            if v == w:
                workVacDays = workVacDays + 1

    # Подсчет среднего времени на работе
    everydayWorkTime = 0
    currentDayWorkTime = []
    currentDayTime = 0
    for n in range(numOfDays):
        for sorRow in sorResult:
            if sorRow[3].day == workDays[n]:
                currentDayWorkTime.append(sorRow)
        for i in range(len(currentDayWorkTime) - 1):
            if currentDayWorkTime[i][2] == 2 and currentDayWorkTime[i + 1][2] == 1:
                currentDayTime = currentDayTime + (
                            currentDayWorkTime[i + 1][3].hour * 3600 + currentDayWorkTime[i + 1][3].minute * 60 +
                            currentDayWorkTime[i + 1][3].second) - (currentDayWorkTime[i][3].hour * 3600 +
                                                                    currentDayWorkTime[i][3].minute * 60 +
                                                                    currentDayWorkTime[i][3].second)
        everydayWorkTime = everydayWorkTime + currentDayTime
        currentDayWorkTime.clear()
        currentDayTime = 0

    if numOfDays > 0:
        middleEverydayWorkTimeinSeconds = round(everydayWorkTime / numOfDays)
    else:
        middleEverydayWorkTimeinSeconds = 0

    # Собирание времени прибытий/уходов
    everydayArrival = []
    everydayDeparture = []

    for n in range(numOfDays):
        for sorRow in sorResult:
            if sorRow[3].day == workDays[n]:
                everydayArrival.append(sorRow[3])
                break
        for sorRow in reversed(sorResult):
            if sorRow[3].day == workDays[n]:
                everydayDeparture.append(sorRow[3])
                break

    # Пересчет в секунды
    ArrivalSeconds = 0
    DepartureSeconds = 0
    for day in everydayArrival:
        ArrivalSeconds = ArrivalSeconds + day.hour * 3600 + day.minute * 60 + day.second

    for day in everydayDeparture:
        DepartureSeconds = DepartureSeconds + day.hour * 3600 + day.minute * 60 + day.second

    if numOfDays > 0:
        midArrivalSecond = round(ArrivalSeconds / numOfDays)
        midDepartureSecond = round(DepartureSeconds / numOfDays)
    else:
        midArrivalSecond = 0
        midDepartureSecond = 0

    # Пересчет в часы
    def secondTotime(seconds):
        Hour = seconds // 3600
        Minute = (seconds - Hour * 3600) // 60
        Second = seconds - Minute * 60 - Hour * 3600
        string = str(Hour) + ":" + str(Minute) + ":" + str(Second)
        return string

    # Подсчет среднего времени вне работы
    midWalkTime = midDepartureSecond - midArrivalSecond - middleEverydayWorkTimeinSeconds

    calculateResult = [numOfDays,secondTotime(midArrivalSecond),secondTotime(midDepartureSecond),secondTotime(middleEverydayWorkTimeinSeconds),
                       len(vacDays),workVacDays,secondTotime(midWalkTime)]

    mycursor.close
    myconnection.close

    return calculateResult
