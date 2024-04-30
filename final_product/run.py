from project import create_app

if __name__ == "__main__":
    host, port = "0.0.0.0", 8080
    create_app().run(host= host, port= port, debug=True)
    print(f"Server now running at {host}:{port}")