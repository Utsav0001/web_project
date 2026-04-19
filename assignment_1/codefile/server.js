const express = require("express");
const cors = require("cors");
const path = require("path");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const PORT = process.env.PORT || 4000;

/* DATABASE */

const dbPath = path.join(__dirname, "db.sqlite");
const db = new sqlite3.Database(dbPath);

/* FRONTEND */

const frontendPath = path.join(__dirname, "..", "frontend");

/* MIDDLEWARE */

app.use(cors());
app.use(express.json());
app.use(express.static(frontendPath));

/* CREATE TABLE */

db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS tasks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      description TEXT DEFAULT '',
      priority TEXT DEFAULT 'Medium',
      isDone INTEGER DEFAULT 0,
      createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
});

/* HELPERS */

function normalizeTask(row) {
  return {
    ...row,
    isDone: Boolean(row.isDone),
  };
}

function validateTitle(title) {
  return (
    typeof title === "string" &&
    title.trim().length > 0 &&
    title.trim().length <= 50
  );
}

function validatePriority(priority) {
  return ["Low", "Medium", "High"].includes(priority);
}

/* GET ALL TASKS */

app.get("/tasks", (req, res) => {

  db.all(
    "SELECT id,title,description,priority,isDone,createdAt FROM tasks",
    [],
    (error, rows) => {

      if (error) {
        return res.status(500).json({ message: "Failed to fetch tasks." });
      }

      const tasks = rows.map(normalizeTask);

      res.json(tasks);
    }
  );
});

/* CREATE TASK */

app.post("/tasks", (req, res) => {

  const { title, description = "", priority = "Medium" } = req.body;

  if (!validateTitle(title)) {
    return res.status(400).json({
      message: "Title must be between 1 and 50 characters",
    });
  }

  if (!validatePriority(priority)) {
    return res.status(400).json({
      message: "Priority must be Low, Medium, or High",
    });
  }

  const query =
    "INSERT INTO tasks (title,description,priority) VALUES (?,?,?)";

  db.run(
    query,
    [title.trim(), description.trim(), priority],
    function (error) {

      if (error) {
        return res.status(500).json({ message: "Failed to create task" });
      }

      db.get(
        "SELECT id,title,description,priority,isDone,createdAt FROM tasks WHERE id = ?",
        [this.lastID],
        (err, row) => {

          if (err) {
            return res.status(500).json({ message: "Task created but fetch failed" });
          }

          res.status(201).json(normalizeTask(row));
        }
      );
    }
  );
});

/* UPDATE TASK */

app.put("/tasks/:id", (req, res) => {

  const { id } = req.params;
  const { title, description = "", priority = "Medium" } = req.body;

  if (!validateTitle(title)) {
    return res.status(400).json({ message: "Invalid title" });
  }

  if (!validatePriority(priority)) {
    return res.status(400).json({ message: "Invalid priority" });
  }

  const query =
    "UPDATE tasks SET title=?,description=?,priority=? WHERE id=?";

  db.run(
    query,
    [title.trim(), description.trim(), priority, id],
    function (error) {

      if (error) {
        return res.status(500).json({ message: "Failed to update task" });
      }

      if (this.changes === 0) {
        return res.status(404).json({ message: "Task not found" });
      }

      db.get(
        "SELECT id,title,description,priority,isDone,createdAt FROM tasks WHERE id=?",
        [id],
        (err, row) => {

          if (err) {
            return res.status(500).json({ message: "Task updated but fetch failed" });
          }

          res.json(normalizeTask(row));
        }
      );
    }
  );
});

/* TOGGLE STATUS */

app.patch("/tasks/:id/status", (req, res) => {

  const { id } = req.params;
  const { isDone } = req.body;

  if (typeof isDone !== "boolean") {
    return res.status(400).json({ message: "isDone must be boolean" });
  }

  db.run(
    "UPDATE tasks SET isDone=? WHERE id=?",
    [isDone ? 1 : 0, id],
    function (error) {

      if (error) {
        return res.status(500).json({ message: "Failed to update status" });
      }

      if (this.changes === 0) {
        return res.status(404).json({ message: "Task not found" });
      }

      db.get(
        "SELECT id,title,description,priority,isDone,createdAt FROM tasks WHERE id=?",
        [id],
        (err, row) => {

          if (err) {
            return res.status(500).json({ message: "Status updated but fetch failed" });
          }

          res.json(normalizeTask(row));
        }
      );
    }
  );
});

/* DELETE TASK */

app.delete("/tasks/:id", (req, res) => {

  const { id } = req.params;

  db.run(
    "DELETE FROM tasks WHERE id=?",
    [id],
    function (error) {

      if (error) {
        return res.status(500).json({ message: "Failed to delete task" });
      }

      if (this.changes === 0) {
        return res.status(404).json({ message: "Task not found" });
      }

      res.status(204).send();
    }
  );
});

/* FRONTEND ROUTE */

app.get("*", (req, res) => {
  res.sendFile(path.join(frontendPath, "index.html"));
});

/* START SERVER */

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

/* CLOSE DATABASE */

process.on("SIGINT", () => {
  db.close(() => {
    process.exit(0);
  });
});