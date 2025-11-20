from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', events=[])

@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        
       # TODO: handle formsubmission
        pass

    return render_template('add_event.html')
if __name__ == '__main__':
    app.run(debug=True)


    