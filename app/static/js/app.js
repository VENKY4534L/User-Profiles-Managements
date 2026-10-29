document.addEventListener("click", function (event) {
  const button = event.target.closest("[data-delete-form]");
  if (!button) return;
  const form = document.getElementById(button.getAttribute("data-delete-form"));
  if (form && window.confirm("Delete this user? This action cannot be undone.")) form.requestSubmit();
});
