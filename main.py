import datetime
import random

import mysql.connector
from mysql.connector import Error
from flask import *


# SQL
table = ""
# SQL


# HTML
app = Flask(__name__)

# Шаблоны
authorization_template = "authorization.html"
user_template = "user.html"
admin_template = "admin.html"
game_template = "game.html"
row_template = "row.html"
add_template = "add.html"
# Шаблоны
# HTML


# Translation
genre_rus = {
    "Action": "Экшен",
    "Simulator": "Симулятор",
    "Arcade": "Аркада",
    "RPG": "Ролевое",
    "Strategy": "Стратегия",
    "Quest": "Головоломка",
    "Other": "Другое"
}
age_rating_rus = {
    "EC": "0+",
    "E": "6+",
    "E10+": "10+",
    "T": "13+",
    "M": "16+",
    "AO": "18+"
}
table_rus = {
    "employee": "Работники",
    "game": "Игры",
    "library": "Библиотеки",
    "position": "Должности",
    "publisher": "Издатели",
    "refund": "Возвраты",
    "sell": "Продажи",
    "user": "Пользователи"
}
# Translation


# SQL
def connect_database():
    global connection

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="SmartPassword",
            database="game_shop"
        )
    except Error as e:
        print(e)

    return connection


def execute_query(query):
    global connection

    cursor = connection.cursor()
    try:
        cursor.execute(query)

        connection.commit()
    except Error as e:
        print(e)

        return "% ошибка %", e


def execute_read_query(query):
    global connection

    cursor = connection.cursor()
    try:
        cursor.execute(query)

        result = cursor.fetchall()

        final_result = [list(i) for i in result]

        return final_result
    except Error as e:
        print(e)
# SQL


# HTML
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        print(request.form)
        if "log_user" in request.form:
            username = request.form["username"]
            password = request.form["password"]

            if execute_read_query(f"SELECT check_login('{username}', '{password}')")[0][0] == 2:
                return redirect(f"http://127.0.0.1:5000/admin/")
            elif execute_read_query(f"SELECT check_login('{username}', '{password}')")[0][0] == 1:
                return redirect(f"http://127.0.0.1:5000/user/{username}/")
            else:
                return render_template(authorization_template, state="login", title="Авторизация", Previous_attempt=False)

        if "reg_user" in request.form:
            username = request.form["username_reg"]
            password = request.form["password_reg"]
            email = request.form["email_reg"]

            if execute_read_query(f"SELECT check_register('{username}', '{email}')")[0][0] == 0 and (username != "" and password != "" and email != ""):
                execute_query(f"INSERT INTO user(username, password, email) VALUES ('{username}', '{password}', '{email}')")
                return redirect(f"http://127.0.0.1:5000/user/{username}/")
            else:
                return render_template(authorization_template, state="register", title="Регистрация", Previous_attempt=False)
        if "log_user_change" in request.form:
            return render_template(authorization_template, state="login", title="Авторизация")
        if "reg_user_change" in request.form:
            return render_template(authorization_template, state="register", title="Регистрация")


    return render_template(authorization_template, state="login", title = "Авторизация")


@app.route("/user/<string:name>/", methods=["POST", "GET"])
def user(name):
    user_id = execute_read_query(f"SELECT id FROM user WHERE username = '{name}'")[0][0]
    profile = execute_read_query(f"SELECT * FROM user WHERE username='{name}'")[0]
    games = execute_read_query("SELECT * FROM game ORDER BY name")
    library = execute_read_query(f"SELECT * FROM game as g JOIN library as l ON l.game_id=g.id JOIN user as u ON u.id=l.user_id WHERE l.user_id={user_id}")
    print(profile)
    # Translation
    games = translation(True, games, "game")
    error = ""
    # Translation
    # ТЕСТ
    if request.method == "POST":
        print(request.form)
        if "exit" in request.form:
            return redirect(f"http://127.0.0.1:5000/")
        if "profile" in request.form:
            return render_template(user_template, username=name, state="profile", profile=profile)
        if "search" in request.form:
            empty_games = False
            game_name = request.form["new value 1"]
            genre = request.form["new value 2"]
            left_price = request.form["new value 3"]
            right_price = request.form["new value 4"]
            game_name = '%' + game_name + '%'
            if left_price == "":
                left_price = None
            if right_price == "":
                left_price = None
            print(game_name)
            print(left_price)
            games = execute_read_query(f"CALL sort_games('{game_name}', '{genre}', {left_price}, {right_price})")
            print(games)
            games = translation(True, games, "game")
            if len(games) == 0:
                empty_games = True
            connect_database()
            return render_template(user_template, username=name, state="shop", games=games, empty_games=empty_games)
        if "shop" in request.form:
            print(games)
            return render_template(user_template, username=name, state="shop", games=games)
        if "library" in request.form:
            print(library)
            return render_template(user_template, username=name, state="library", library=library)
        if "change username" in request.form:
            return render_template(user_template, username=name, state="profile", profile=profile, modal=True, change="Никнейм")
        if "change password" in request.form:
            return render_template(user_template, username=name, state="profile", profile=profile, modal=True, change="Пароль")
        if "change email" in request.form:
            return render_template(user_template, username=name, state="profile", profile=profile, modal=True, change="Адрес электронной почты")
        if "change phone_number" in request.form:
            return render_template(user_template, username=name, state="profile", profile=profile, modal=True, change="Номер телефона")
        if "change birth_date" in request.form:
            return render_template(user_template, username=name, state="profile", profile=profile, modal=True, change="Дата рождения")
        if "decide fill wallet" in request.form:
            return render_template(user_template, username=name, state="profile", profile=profile, wallet=True)
        if "fill wallet" in request.form:
            value = request.form["new value"]
            try:
                value = int(value)
            except:
                pass
            print(type(value))
            if isinstance(value, str):
                error = "Введена некорректная сумма"
                return render_template(user_template, username=name, state="profile", profile=profile, error=error)
            else:
                if value <= 0:
                    #if execute_read_query(f"SELECT check_fill({value})")[0][0] == 0:
                    error = "Введена некорректная сумма"
                    return render_template(user_template, username=name, state="profile", profile=profile, error=error)
                    #if execute_query(f"UPDATE user SET birth_date='{value}' WHERE username='{name}'") != None:
                    #    error = str(execute_query(f"UPDATE user SET birth_date='{value}' WHERE username='{name}'")[1])
                    #    return render_template(user_template, username=name, state="profile", profile=profile, error=error)
                else:
                    #execute_query(f"UPDATE user SET birth_date=NULL WHERE username='{name}'")
                    wallet = execute_read_query(f"SELECT wallet FROM user WHERE username='{name}'")
                    value = wallet[0][0] + value
                    execute_query(f"UPDATE user SET wallet={value} WHERE username='{name}'")
            return redirect(f"http://127.0.0.1:5000/user/{name}/")
        if "select Никнейм" in request.form:
            value = request.form["new value"]
            if value != "":
                if execute_query(f"UPDATE user SET username='{value}' WHERE username='{name}'") != None:
                    error = str(execute_query(f"UPDATE user SET username='{value}' WHERE username='{name}'")[1])
                    return render_template(user_template, username=name, state="profile", profile=profile, error=error)
                else:
                    return redirect(f"http://127.0.0.1:5000/user/{value}/")
            else:
                return redirect(f"http://127.0.0.1:5000/user/{name}/")
        if "select Пароль" in request.form:
            value = request.form["new value"]
            if value != "":
                execute_query(f"UPDATE user SET password='{value}' WHERE username='{name}'")
            return redirect(f"http://127.0.0.1:5000/user/{name}/")
        if "select Адрес электронной почты" in request.form:
            value = request.form["new value"]
            if value != "":
                execute_query(f"UPDATE user SET email='{value}' WHERE username='{name}'")
            return redirect(f"http://127.0.0.1:5000/user/{name}/")
        if "select Номер телефона" in request.form:
            value = request.form["new value"]
            if value != "":
                if execute_query(f"UPDATE user SET phone_number='{value}' WHERE username='{name}'") != None:
                    error = str(execute_query(f"UPDATE user SET phone_number='{value}' WHERE username='{name}'")[1])
                    return render_template(user_template, username=name, state="profile", profile=profile, error=error)
            return redirect(f"http://127.0.0.1:5000/user/{name}/")
        if "select Дата рождения" in request.form:
            value = request.form["new value"]
            if value != "":
                if execute_query(f"UPDATE user SET birth_date='{value}' WHERE username='{name}'") != None:
                    error = str(execute_query(f"UPDATE user SET birth_date='{value}' WHERE username='{name}'")[1])
                    return render_template(user_template, username=name, state="profile", profile=profile, error=error)
            else:
                execute_query(f"UPDATE user SET birth_date=NULL WHERE username='{name}'")
            return redirect(f"http://127.0.0.1:5000/user/{name}/")
        if "select" in request.form:
            print(request.form["new value"])
            return render_template(user_template, username=name, state="profile", profile=profile, error=error)
    else:
        return render_template(user_template, username=name, state="profile", profile=profile, error=error)
    # ТЕСТ


@app.route("/refund/<string:name>/<int:id>/")
def refund(name, id):
    print(1)
    user_id = execute_read_query(f"SELECT id FROM user WHERE username = '{name}'")[0][0]
    wallet = execute_read_query(f"SELECT wallet FROM user WHERE id = {user_id}")[0][0]
    price = execute_read_query(f"SELECT price FROM game WHERE id = {id}")[0][0]
    wallet = wallet + price
    execute_query(f"UPDATE user SET wallet={wallet} WHERE username='{name}'")
    execute_query(f"DELETE FROM library WHERE user_id={user_id} AND game_id={id}")
    execute_query(f"CALL do_refund({user_id}, {id})")
    return redirect(f"http://127.0.0.1:5000/user/{name}/")

@app.route("/user/<string:name>/buy_game/<int:id>/", methods=["POST", "GET"])
def game(name, id):
    #print(name)
    user_id = execute_read_query(f"SELECT id FROM user WHERE username = '{name}'")[0][0]
    game = execute_read_query(f"SELECT * FROM game WHERE id={id}")[0]
    # Translation
    game = translation(False, game, "game")
    # Translation
    #print(type(game[0]))
    game_name = execute_read_query(f"SELECT name FROM game WHERE id = {game[0]}")[0][0]
    publisher = execute_read_query(f"SELECT p.name FROM publisher AS p JOIN game AS g ON g.publisher_id = p.id WHERE g.id = {game[0]}")[0][0]
    #(publisher)
    #print(game)
    is_purchased = execute_read_query(f"SELECT check_purchased({user_id}, {id})")[0][0]
    print(is_purchased)
    if request.method == "POST":
        print(request.form)
        if "purchase" in request.form:
            if execute_read_query(f"SELECT check_age('{user_id}', '{id}')")[0][0] == 1:
                wallet = execute_read_query(f"SELECT wallet FROM user WHERE id = {user_id}")[0][0]
                price = execute_read_query(f"SELECT price FROM game WHERE id = {game[0]}")[0][0]
                if price > wallet:
                    return render_template(game_template, game=game, name=game_name, publisher=publisher, purchased=True, price=True)
                else:
                    wallet = wallet - price
                    execute_query(f"UPDATE user SET wallet={wallet} WHERE username='{name}'")
                    execute_query(f"INSERT INTO library(user_id, game_id) VALUES ({user_id}, {id})")
                    time = datetime.datetime.now()
                    execute_query(f"INSERT INTO sell(user_id, game_id, deal_datetime, payment_method) VALUES ({user_id}, {id}, '{time}', {random.randint(1,3)})")
                return render_template(game_template, game=game, name=game_name, publisher=publisher, purchased=True)
            else:
                return render_template(game_template, game=game, name=game_name, publisher=publisher, purchased=True, age=True)
        if "exit" in request.form:
            return redirect(f"http://127.0.0.1:5000/user/{name}/")
    return render_template(game_template, game=game, name=game_name, publisher=publisher, purchased=is_purchased)


@app.route("/admin/", methods=["POST", "GET"])
def admin():
    size = [0, 1, 2, 3, 4, 5, 6, 7]
    tables_list = execute_read_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'game_shop'")
    tables_list_new = execute_read_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'game_shop'")
    tables_list_rus = translation(True, tables_list_new, "tables")
    list = execute_read_query("SELECT * FROM game")
    if request.method == "POST":
        print(request.form)
        if "exit" in request.form:
            return redirect(f"http://127.0.0.1:5000/")
        if "employee" in request.form:
            list = execute_read_query("SELECT * FROM employee")
            print(list)
            for row in list:
                row[1] = execute_read_query(f"SELECT find_position({row[0]})")[0][0]
            return render_template(admin_template, tables_list=tables_list, tables_list_rus=tables_list_rus, size=size, chosed_table="employee", list=list)
        if "game" in request.form:
            list = execute_read_query("SELECT * FROM game")
            print(list)
            list = translation(True, list, "game")
            for row in list:
                row[5] = execute_read_query(f"SELECT find_publisher({row[0]})")[0][0]
            return render_template(admin_template, tables_list=tables_list, tables_list_rus=tables_list_rus, size=size, chosed_table="game", list=list)
        if "library" in request.form:
            list = execute_read_query("SELECT * FROM library")
            print(list)
            for row in list:
                row[1] = execute_read_query(f"SELECT find_user({row[1]}, 'library')")[0][0]
                row[2] = execute_read_query(f"SELECT find_game({row[2]}, 'library')")[0][0]
            return render_template(admin_template, tables_list=tables_list, tables_list_rus=tables_list_rus, size=size, chosed_table="library", list=list)
        if "position" in request.form:
            list = execute_read_query("SELECT * FROM position")
            print(list)
            return render_template(admin_template, tables_list=tables_list, tables_list_rus=tables_list_rus, size=size, chosed_table="position", list=list)
        if "publisher" in request.form:
            list = execute_read_query("SELECT * FROM publisher")
            print(list)
            for row in list:
                row[2] = str(row[2] * 100) + "%"
            return render_template(admin_template, tables_list=tables_list, tables_list_rus=tables_list_rus, size=size, chosed_table="publisher", list=list)
        if "refund" in request.form:
            list = execute_read_query("SELECT * FROM refund")
            for row in list:
                sell = execute_read_query(f"SELECT * FROM sell WHERE id={row[0]}")[0]
                print(sell)
                row.append("")
                row[3] = "Пользователь " + execute_read_query(f"SELECT find_user({sell[1]}, 'sell')")[0][0] + " вернул " + execute_read_query(f"SELECT find_game({sell[2]}, 'sell')")[0][0]
                if execute_read_query(f"SELECT find_employee_info({row[1]}, 4)")[0][0] != None or execute_read_query(f"SELECT find_employee_info({row[1]}, 4)")[0][0] != "":
                    row[1] = execute_read_query(f"SELECT find_employee_info({row[1]}, 3)")[0][0] + " "\
                             + execute_read_query(f"SELECT find_employee_info({row[1]}, 2)")[0][0] + " "\
                             + execute_read_query(f"SELECT find_employee_info({row[1]}, 4)")[0][0] + ", "\
                             + execute_read_query(f"SELECT find_employee_info({row[1]}, 1)")[0][0]
                else:
                    row[1] = execute_read_query(f"SELECT find_employee_info({row[1],}, 3)")[0][0] + " " \
                             + execute_read_query(f"SELECT find_employee_info({row[1]}, 2)")[0][0] + ", " \
                             + execute_read_query(f"SELECT find_employee_info({row[1]}, 1)")[0][0]
                row[2] = str(row[2])[2:10] + " в " + str(row[2])[11:]
            return render_template(admin_template, tables_list=tables_list, tables_list_rus=tables_list_rus, size=size, chosed_table="refund", list=list)
        if "sell" in request.form:
            list = execute_read_query("SELECT * FROM sell")
            print(list)
            for row in list:
                row[1] = execute_read_query(f"SELECT find_user({row[1]}, 'sell')")[0][0]
                row[2] = execute_read_query(f"SELECT find_game({row[2]}, 'sell')")[0][0]
            return render_template(admin_template, tables_list=tables_list, tables_list_rus=tables_list_rus, size=size, chosed_table="sell", list=list)
        if "user" in request.form:
            list = execute_read_query("SELECT * FROM user")
            print(list)
            for row in list:
                if row[4] == None or row[4] == "":
                    row[4] = "Отсутствует"
                if row[5] == None or row[5] == "":
                    row[5] = "Отсутствует"
                if row[7] == 1:
                    row[7] = "Да"
                else:
                    row[7] = "Нет"
            return render_template(admin_template, tables_list=tables_list, tables_list_rus=tables_list_rus, size=size, chosed_table="user", list=list)
    list = translation(True, list, "game")
    for row in list:
        row[5] = execute_read_query(f"SELECT find_publisher({row[0]})")[0][0]
    return render_template(admin_template, tables_list=tables_list, tables_list_rus=tables_list_rus, size=size, chosed_table="game", list=list)


@app.route("/admin/<string:table>/<int:id>/", methods=["POST", "GET"])
def view_row(table, id):
    error = ""
    change = False
    if request.method == "POST":
        print(request.form)
        if "exit" in request.form:
            return redirect(f"http://127.0.0.1:5000/admin/")
        if "delete" in request.form:
            execute_query(f"DELETE FROM {table} WHERE id={id}")
            return redirect(f"http://127.0.0.1:5000/admin/")
        if "change" in request.form:
            change = True
        if "confirm change" in request.form:
            if table == "employee":
                column1 = request.form["new 1"]
                column2 = request.form["new 2"]
                column3 = request.form["new 3"]
                column4 = request.form["new 4"]
                if(execute_query(f"UPDATE employee "
                                    f"SET position_id = {column1}, "
                                    f"name = '{column2}', "
                                    f"surname = '{column3}', "
                                    f"patronymic = '{column4}' "
                                    f"WHERE id={id}")) != None:
                    error = str(execute_query(f"UPDATE employee "
                                    f"SET position_id = {column1}, "
                                    f"name = '{column2}', "
                                    f"surname = '{column3}', "
                                    f"patronymic = '{column4}' "
                                    f"WHERE id={id}")[1])
            if table == "game":
                column1 = request.form["new 1"]
                column2 = request.form["new 2"]
                column3 = request.form["new 3"]
                column4 = request.form["new 4"]
                column5 = request.form["new 5"]
                if(execute_query(f"UPDATE game "
                                    f"SET name = '{column1}', "
                                    f"price = {column2}, "
                                    f"genre = '{column3}', "
                                    f"age_rating = '{column4}', "
                                    f"publisher_id = {column5} "
                                    f"WHERE id={id}")) != None:
                    error = str(execute_query(f"UPDATE game "
                                    f"SET name = '{column1}', "
                                    f"price = {column2}, "
                                    f"genre = '{column3}', "
                                    f"age_rating = '{column4}', "
                                    f"publisher_id = {column5} "
                                    f"WHERE id={id}")[1])
            if table == "position":
                column1 = request.form["new 1"]
                column2 = request.form["new 2"]
                if(execute_query(f"UPDATE position "
                                    f"SET title = '{column1}', "
                                    f"salary = {column2} "
                                    f"WHERE id={id}")) != None:
                    error = str(execute_query(f"UPDATE position "
                                    f"SET title = '{column1}', "
                                    f"salary = {column2} "
                                    f"WHERE id={id}")[1])
            if table == "publisher":
                column1 = request.form["new 1"]
                column2 = request.form["new 2"]
                if(execute_query(f"UPDATE publisher "
                                    f"SET name = '{column1}', "
                                    f"interest_rate = {column2} "
                                    f"WHERE id={id}")) != None:
                    error = str(execute_query(f"UPDATE publisher "
                                    f"SET name = '{column1}', "
                                    f"interest_rate = {column2} "
                                    f"WHERE id={id}")[1])
            if table == "user":
                column1 = request.form["new 1"]
                column2 = request.form["new 2"]
                column3 = request.form["new 3"]
                column4 = request.form["new 4"]
                column5 = request.form["new 5"]
                column6 = request.form["new 6"]
                print(column1, column2, column3, column4, column5, column6)
                if(execute_query(f"UPDATE user "
                                    f"SET username = '{column1}', "
                                    f"password = '{column2}', "
                                    f"email = '{column3}', "
                                    f"phone_number = '{column4}', "
                                    f"birth_date = '{column5}', "
                                    f"admin = {column6} "
                                    f"WHERE id={id}")) != None:
                    error = str(execute_query(f"UPDATE user "
                                    f"SET username = '{column1}', "
                                    f"password = '{column2}', "
                                    f"email = '{column3}', "
                                    f"phone_number = '{column4}', "
                                    f"birth_date = '{column5}', "
                                    f"admin = {column6} "
                                    f"WHERE id={id}")[1])
    table_list = execute_read_query(f"SELECT * FROM {table}")
    rus_table = table_rus.get(table)
    #print(rus_table)
    id = id - 1
    print(id)
    index = 0
    for row in table_list:
        if id == row[0] - 1:
            id = index
        index += 1
    if table == "employee":
        if table_list[id][4] == None or table_list[id][4] == "":
            table_list[id][4] = "Отсутствует"
    if table == "user":
        if table_list[id][4] == None or table_list[id][4] == "":
            table_list[id][4] = "Отсутствует"
        if table_list[id][5] == None or table_list[id][5] == "":
            table_list[id][5] = "Отсутствует"
    print(id)
    print(table_list)
    return render_template(row_template, table_name=table, table=table_list, id=id, table_rus=rus_table, change=change, error=error)
# HTML


@app.route("/admin/<string:table>/add/", methods=["POST", "GET"])
def add(table):
    error = ""
    rus_table = table_rus.get(table)
    if request.method == "POST":
        print(request.form)
        if "exit" in request.form:
            return redirect(f"http://127.0.0.1:5000/admin/")
        if "add" in request.form:
            if table == "employee":
                column1 = request.form["new 1"]
                column2 = request.form["new 2"]
                column3 = request.form["new 3"]
                column4 = request.form["new 4"]
                print(column1, column2, column3, column4)
                if execute_query(f"INSERT INTO employee(position_id, name, surname, patronymic) VALUES ({column1}, '{column2}', '{column3}', '{column4}')") != None:
                    error = str(execute_query(f"INSERT INTO employee(position_id, name, surname, patronymic) VALUES ({column1}, '{column2}', '{column3}', '{column4}')")[1])
                    return render_template(add_template, table=table, table_rus=rus_table, error=error)
                return redirect(f"http://127.0.0.1:5000/admin/")
            if table == "game":
                column1 = request.form["new 1"]
                column2 = request.form["new 2"]
                column3 = request.form["new 3"]
                column4 = request.form["new 4"]
                column5 = request.form["new 5"]
                print(column1, column2, column3, column4, column5)
                if(execute_query(f"INSERT INTO game(name, price, genre, age_rating, publisher_id) VALUES ('{column1}', {column2}, '{column3}', '{column4}', {column5})")) != None:
                    error = str(execute_query(f"INSERT INTO game(name, price, genre, age_rating, publisher_id) VALUES ('{column1}', {column2}, '{column3}', '{column4}', {column5})")[1])
                    return render_template(add_template, table=table, table_rus=rus_table, error=error)
                return redirect(f"http://127.0.0.1:5000/admin/")
            if table == "position":
                column1 = request.form["new 1"]
                column2 = request.form["new 2"]
                print(column1, column2)
                if(execute_query(f"INSERT INTO position (title, salary) VALUES ('{column1}', {column2})")) != None:
                    error = str(execute_query(f"INSERT INTO position (title, salary) VALUES ('{column1}', {column2})")[1])
                    return render_template(add_template, table=table, table_rus=rus_table, error=error)
                return redirect(f"http://127.0.0.1:5000/admin/")
            if table == "publisher":
                column1 = request.form["new 1"]
                column2 = request.form["new 2"]
                print(column1, column2)
                if(execute_query(f"INSERT INTO publisher(name, interest_rate) VALUES ('{column1}', {column2})")) != None:
                    error = str(execute_query(f"INSERT INTO publisher(name, interest_rate) VALUES ('{column1}', {column2})")[1])
                    return render_template(add_template, table=table, table_rus=rus_table, error=error)
                return redirect(f"http://127.0.0.1:5000/admin/")
    print(table)
    return render_template(add_template, table=table, table_rus=rus_table)


def translation(is_table, list_table, table_name):
    if is_table:
        if table_name == "game":
            for row in list_table:
                row[3] = genre_rus.get(row[3])
                row[4] = age_rating_rus.get(row[4])
        if table_name == "tables":
            for row in list_table:
                #print(row[0])
                row[0] = table_rus.get(row[0])
    else:
        if table_name == "game":
            list_table[3] = genre_rus.get(list_table[3])
            list_table[4] = age_rating_rus.get(list_table[4])
        if table_name == "tables":
            list_table[0] = table_rus.get(list_table[0])

    return list_table


connection = connect_database()

if __name__ == "__main__":
    app.run(debug=True)