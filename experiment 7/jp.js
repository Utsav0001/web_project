const products=[
{id:1,name:"Laptop",price:50000,desc:"Powerful laptop"},
{id:2,name:"Phone",price:20000,desc:"Smartphone"},
{id:3,name:"Headphones",price:3000,desc:"Wireless sound"}
];

let cart=[];

function renderProducts(){
const div=document.getElementById("products");
products.forEach(p=>{
div.innerHTML+=`
<div class="card">
<h3>${p.name}</h3>
<p>${p.desc}</p>
<p>₹${p.price}</p>
<button onclick="addToCart(${p.id})">Add to Cart</button>
</div>`;
});
}

function addToCart(id){
let item=cart.find(c=>c.id===id);
if(item)item.qty++;
else{
let product=products.find(p=>p.id===id);
cart.push({...product,qty:1});
}
updateCart();
}

function removeItem(id){
cart=cart.filter(i=>i.id!==id);
updateCart();
}

function updateCart(){
let cartDiv=document.getElementById("cart");
cartDiv.innerHTML="";
let total=0;

cart.forEach(i=>{
total+=i.price*i.qty;
cartDiv.innerHTML+=`
<p>${i.name} x${i.qty}
<button onclick="removeItem(${i.id})">Remove</button></p>`;
});

document.getElementById("total").innerText=total;
}

function checkout(){
document.getElementById("msg").innerText=
"Order placed successfully!";
cart=[];
updateCart();
}

renderProducts();
