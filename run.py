import optparse

from app import app

# Set up the command-line options
parser = optparse.OptionParser()
parser.add_option(
    "-H",
    "--host",
    help="Host of the Flask-app default: 0.0.0.0",
    default='0.0.0.0'
)
parser.add_option(
    "-P",
    "--port",
    help="Port for the Flask-app default: 5000",
    default=5000
)
parser.add_option(
    "--nd",
    "--nodebug",
    action="store_false",
    dest="debug",
    help="Disable debug-mode for Flask-app",
    default=app.config['DEBUG']
)
options, _ = parser.parse_args()


if __name__ == '__main__':
    app.run(
        debug=options.debug,
        host=options.host,
        port=int(options.port)
    )
