from flask import Flask,render_template,jsonify
from flaskext.mysql import MySQL
import json
app = Flask(__name__)


mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'meacrouwro'
app.config['MYSQL_DATABASE_DB'] = 'tweet_data'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/")
def main():
    cur = mysql.connect().cursor()
    cur.execute("SELECT `name`, DATE(`created_at`),`id` FROM `trends` ORDER BY `created_at` DESC LIMIT 7")
    trends=cur.fetchall()
    return render_template('index.html', trends=trends)


@app.route("/trend/<trend>")
def show_entities(trend):

    cur = mysql.connect().cursor()
    query = "SELECT `entity` as Entity, COUNT(`entity`) AS Count FROM `data` WHERE `trend`=%s AND `entity` IS NOT NULL " \
            " AND `entity` NOT LIKE %s GROUP BY `entity`" \
            " ORDER BY COUNT(`entity`) DESC LIMIT 10"
    cur.execute(query, (trend, ('%' + 'Not Found' + '%',) ))
    entities = cur.fetchall()
    payload = []
    content = {}
    for result in entities:
        content = {'Entity': result[0], 'Count': result[1]}
        payload.append(content)
        content = {}
    query = "SELECT `name` FROM `trends` WHERE `id`=%s"
    cur.execute(query, trend)
    name = cur.fetchall()
    return render_template('trend.html', entities=entities, trend = name[0], chart_data = json.dumps(payload))



@app.route("/date/<date>")
def show_day(date):
    return 'Summary on %s' % date

if __name__ == "__main__":
    app.debug = True
    app.run()
