from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

contacts = [
    {"id":1,"name":"Utsav","phone":"9999999999","email":"utsav@gmail.com"}
]

@app.route("/")
def home():
    query = request.args.get("search","").lower()
    filtered = [c for c in contacts if query in c["name"].lower() or query in c["phone"]]
    return render_template("index.html", contacts=filtered)

@app.route("/add", methods=["GET","POST"])
def add():
    if request.method=="POST":
        name=request.form["name"]
        phone=request.form["phone"]
        email=request.form["email"]

        if name and phone and email:
            new_id = contacts[-1]["id"]+1 if contacts else 1
            contacts.append({"id":new_id,"name":name,"phone":phone,"email":email})
            return redirect(url_for("home"))

    return render_template("add_contact.html")

@app.route("/edit/<int:id>",methods=["GET","POST"])
def edit(id):
    contact=next((c for c in contacts if c["id"]==id),None)

    if request.method=="POST":
        contact["name"]=request.form["name"]
        contact["phone"]=request.form["phone"]
        contact["email"]=request.form["email"]
        return redirect(url_for("home"))

    return render_template("edit_contact.html",contact=contact)

@app.route("/delete/<int:id>")
def delete(id):
    global contacts
    contacts=[c for c in contacts if c["id"]!=id]
    return redirect(url_for("home"))

if __name__=="__main__":
    app.run(debug=True)
