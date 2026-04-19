const TITLE_LIMIT = 50;

const taskForm = document.getElementById("taskForm");
const taskTitle = document.getElementById("taskTitle");
const taskDescription = document.getElementById("taskDescription");
const taskPriority = document.getElementById("taskPriority");

const taskList = document.getElementById("taskList");
const emptyState = document.getElementById("emptyState");

const taskCounter = document.getElementById("taskCounter");
const activeCounter = document.getElementById("activeCounter");

const taskTemplate = document.getElementById("taskTemplate");

const nodemailer = require("nodemailer");

let tasks = [];

/* LOAD TASKS */

document.addEventListener("DOMContentLoaded", () => {

  const savedTasks = localStorage.getItem("tasks");

  if(savedTasks){
    tasks = JSON.parse(savedTasks);
  }

  renderTasks();
});

/* ADD TASK */

taskForm.addEventListener("submit", function(e){

  e.preventDefault();

  const title = taskTitle.value.trim();
  const description = taskDescription.value.trim();
  const priority = taskPriority.value;

  if(!title){
    alert("Task title required");
    return;
  }

  if(title.length > TITLE_LIMIT){
    alert("Title must be less than 50 characters");
    return;
  }

  const task = {
    id: Date.now(),
    title,
    description,
    priority,
    isDone:false,
    createdAt:new Date()
  };

  tasks.unshift(task);

  saveTasks();

  renderTasks();

  taskForm.reset();
});

/* RENDER TASKS */

function renderTasks(){

  taskList.innerHTML="";

  tasks.forEach(task=>{

    const fragment = taskTemplate.content.cloneNode(true);

    const taskItem = fragment.querySelector(".task-item");
    const checkbox = fragment.querySelector(".task-checkbox");
    const title = fragment.querySelector(".task-title");
    const description = fragment.querySelector(".task-description");
    const date = fragment.querySelector(".task-date");
    const badge = fragment.querySelector(".priority-badge");
    const deleteBtn = fragment.querySelector(".delete-btn");

    title.textContent = task.title;
    description.textContent = task.description || "No description";

    date.textContent = new Date(task.createdAt).toLocaleString();

    badge.textContent = task.priority;

    badge.classList.add(`priority-${task.priority.toLowerCase()}`);

    checkbox.checked = task.isDone;

    taskItem.classList.toggle("completed",task.isDone);

    checkbox.addEventListener("change",()=>{

      task.isDone = checkbox.checked;

      saveTasks();

      renderTasks();
    });

    deleteBtn.addEventListener("click",()=>{

      tasks = tasks.filter(t=>t.id!==task.id);

      saveTasks();

      renderTasks();
    });

    taskList.appendChild(fragment);
  });

  emptyState.style.display = tasks.length ? "none":"block";

  updateCounters();
}

/* SAVE TASKS */

function saveTasks(){

  localStorage.setItem("tasks",JSON.stringify(tasks));
}

/* UPDATE COUNTERS */

function updateCounters(){

  const total = tasks.length;

  const completed = tasks.filter(t=>t.isDone).length;

  taskCounter.textContent = `${completed} / ${total}`;

  activeCounter.textContent = total-completed;
}
const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: "your_email@gmail.com",
    pass: "your_app_password" // NOT your normal password
  }
});


db.run(
  query,
  [title.trim(), description.trim(), priority],
  function (error) {
    const userEmail = req.body.email || "receiver@gmail.com";

const mailOptions = {
  from: "your_email@gmail.com",
  to: userEmail,
  subject: "New Task Created ✅",
  html: `
    <h2>Task Created Successfully</h2>
    <p><b>Title:</b> ${title}</p>
    <p><b>Description:</b> ${description}</p>
    <p><b>Priority:</b> ${priority}</p>
  `
};

transporter.sendMail(mailOptions, (err, info) => {
  if (err) {
    console.log("Email Error:", err);
  } else {
    console.log("Email sent:", info.response);
  }
})
  });