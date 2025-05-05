window.onload = async () => {
  const not_adding_up_msg = document.getElementById("not_adding_up");
  const [
    new_transaction_form,
    new_transaction_form_elements,
    must_name_msg,
    invalid_value_msg
  ] = get_form_stuff();
  const invalid_expense_msg = document.getElementById("invalid_expense");
  const name_field = new_transaction_form_elements[1]
  const expense_field = new_transaction_form_elements[2]
  document.getElementById("new_transaction_button").onclick = async () => {
    if(name_field.value === "") {
      must_name_msg.removeAttribute("hidden");
      invalid_expense_msg.setAttribute("hidden", "");
      invalid_value_msg.setAttribute("hidden", "");
      shake(must_name_msg);
    }
    else if(!(is_money_valid(expense_field.value) && expense_field.value[0] !== "-")) {
      must_name_msg.setAttribute("hidden", "");
      invalid_value_msg.setAttribute("hidden", "");
      invalid_expense_msg.removeAttribute("hidden");
      shake(invalid_expense_msg);
    }
    else if(!all_money_valid(new_transaction_form_elements, 3)) {
      must_name_msg.setAttribute("hidden", "");
      invalid_expense_msg.setAttribute("hidden", "");
      invalid_value_msg.removeAttribute("hidden");
      shake(invalid_value_msg);
    }
    else {
      must_name_msg.setAttribute("hidden", "");
      invalid_expense_msg.setAttribute("hidden", "");
      invalid_value_msg.setAttribute("hidden", "");
      let expense = new_transaction_form_elements[2].value;
      let sum = 0.0;
      let all_filled = true;
      for(let i = 3; i < new_transaction_form_elements.length; i++) {
        if(new_transaction_form_elements[i].value === "") {
          all_filled = false;
          break;
        }
        sum += +(new_transaction_form_elements[i].value);
      }
      sum = sum.toFixed(2);
      expense = (+expense).toFixed(2);
      if(all_filled && sum === expense) {
        new_transaction_form.submit();
      }
      else {
        shake(not_adding_up_msg);
      }
    }
  };
};
