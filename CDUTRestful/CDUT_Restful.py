import sys, os

print(os.path.abspath('..'))
sys.path.append(os.path.abspath('..'))
from CDUTRestful.app import create_app

app = create_app()

@app.route('/')
def get_null_page():
    return 'okokokok'



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=8084, threaded=True)
