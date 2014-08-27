from flask import Flask

app = Flask(__name__)

@app.route('/')
def root():
    return 'Hello, world'

# When testing, allow running of this application directly
if __name__ == '__main__':
    app.run()
