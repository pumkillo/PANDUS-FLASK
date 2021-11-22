function editCom(id_post, id_comment, comtext) {
    text = document.getElementById(id_comment).lastElementChild;
    text.innerHTML = `<form action="/${id_post}/${id_comment}/edit-comm/" method="post">
    <textarea name="text" cols="30" rows="3" class="formcomtext">${comtext}</textarea>
    <button type="submit" class="savebut"><img src="/../static/img/save.png" alt=""></button>
</form>`;
    document.getElementById('editbutton').outerHTML = '';
}     
document.getElementById('check').onclick = function(){
    document.querySelector('#check > input') .checked = !document.querySelector('#check > input') .checked;
}