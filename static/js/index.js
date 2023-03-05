let course = document.getElementById("course");
let faculty = document.getElementById("faculty");

let to_populate = document.getElementById("populate")

selectForm = document.getElementById("selectionCheck")

selectForm.addEventListener('click',()=>{
    
if (course.checked) {
    to_populate.innerHTML = `<form action="">
    <input type="text" name="" id="">
</form>`
  } else if (faculty.checked) {
    to_populate.innerHTML = "Faculty Details"
  } 
  
})
