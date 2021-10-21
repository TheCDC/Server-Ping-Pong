import flask
import random
import requests
import threading


def build_apps(n, chance=0.01):
    for app_id in range(n):
        def make_app(aid):
            """A closure to copy the value of app_id from the for loop."""
            app = flask.Flask(__name__ + str(aid))
            app.config['APP_ID'] = aid

            @app.route('/')
            def root():
                return """<h1>Welcome to server ping pong!</h1>
                <p>You are on server {my_id}<p>
                Click <a href=\"/request\">here</a> to get started.
                """.format(my_id=app.config['APP_ID'])

            @app.route("/request/")
            def request():
                depth = flask.request.args.get('depth')
                if depth is not None:
                    depth = int(depth)
                else:
                    depth = 0

                if random.random() <= chance:

                    return """Request fulfilled by {}. There was a {} chance of exactly this many requests being made.""".format(
                        app.config['APP_ID'],
                        1 - (1 - chance)**(depth))
                else:
                    next_server = random.randint(0, n - 1)
                    next_port = 5000 + next_server
                    url = "http://127.0.0.1:{}/request".format(next_port)
                    message = '{}. {src} is requesting {dest}'.format(
                        depth, src=app.config['APP_ID'], dest=next_server)
                    # print(message)
                    return '<p>{}<p> {} '.format(
                        message,
                        requests.get(url, params={'depth': depth + 1}).text
                    )
            return app
        yield make_app(app_id)


def main():
    ts = []
    for i, a in enumerate(build_apps(10)):
        t = threading.Thread(target=lambda: a.run(
            port=5000 + i, threaded=True))
        t.start()
        ts.append(t)

    for t in ts:
        try:
            t.join()
        except KeyboardInterrupt:
            quit()
    print("yes")


if __name__ == '__main__':
    main()
