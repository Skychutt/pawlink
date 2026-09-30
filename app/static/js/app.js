(function($){"use strict";const token=$("meta[name='csrf-token']").attr("content");$.ajaxSetup({headers:{"X-CSRFToken":token},contentType:"application/json"});window.showToast=function(message,type="success"){const $item=$("<div>").addClass(`flash flash-${type}`).append($("<span>").text(message),$("<button>").text("×"));$(".flash-stack").append($item);setTimeout(()=>$item.fadeOut(200,()=>$item.remove()),3200)};window.apiRequest=function(options){return $.ajax(options).fail(function(xhr){const data=xhr.responseJSON||{};if(xhr.status===401&&data.redirect){window.location=data.redirect;return}window.showToast(data.message||"操作失败，请稍后重试","error")})};$(document).on("click",".flash button",function(){$(this).parent().remove()});$(".nav-toggle").on("click",function(){$(".nav-links,.nav-actions").toggleClass("open")});$(".demo-accounts button").on("click",function(){ $("#account").val($(this).data("account"));$("#password").val($(this).data("password"));});
const LOGIN_KEY="pawlink.login";
const $loginForm=$(".auth-panel form");
if($loginForm.length){
  try{
    const saved=JSON.parse(localStorage.getItem(LOGIN_KEY)||"null");
    if(saved&&saved.account&&!$("#account").val())$("#account").val(saved.account);
    if(saved&&Object.prototype.hasOwnProperty.call(saved,"remember"))$("#remember").prop("checked",!!saved.remember);
  }catch(e){}
  $loginForm.on("submit",function(){
    const remember=$("#remember").prop("checked");
    if(remember)localStorage.setItem(LOGIN_KEY,JSON.stringify({account:$.trim($("#account").val()),remember:true}));
    else localStorage.removeItem(LOGIN_KEY);
  });
}
})(jQuery);
