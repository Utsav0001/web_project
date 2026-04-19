from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

posts = [
    {"id": 1, "title": "First Post", "content": "Welcome to my blog"},
    {"id": 2, "title": "Flask Blog", "content": "Simple CRUD application"}
]

@app.route("/")
def home():
    return render_template("index.html", posts=posts)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        new_id = posts[-1]["id"] + 1 if posts else 1
        posts.append({"id": new_id, "title": title, "content": content})
        return redirect(url_for("home"))
    return render_template("create.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    post = next((p for p in posts if p["id"] == id), None)
    if request.method == "POST":
        post["title"] = request.form["title"]
        post["content"] = request.form["content"]
        return redirect(url_for("home"))
    return render_template("edit.html", post=post)

@app.route("/delete/<int:id>")
def delete(id):
    global posts
    posts = [p for p in posts if p["id"] != id]
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
