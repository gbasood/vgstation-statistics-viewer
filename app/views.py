from app import app, parse

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/test')
def test():
    return parse.parse_url('http://pastebin.com/raw.php?i=ys5QHHZb')
