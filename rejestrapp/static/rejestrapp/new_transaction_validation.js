window.onload = async () => {
  const not_zero_msg = document.getElementById("not_adding_to_zero");
  const [
    new_transaction_form,
    new_transaction_form_elements,
    must_name_msg,
    invalid_value_msg
  ] = get_form_stuff();
  document.getElementById("new_transaction_button").onclick = async () => {
    if(new_transaction_form_elements[1].value === "") {
      invalid_value_msg.setAttribute("hidden", "");
      must_name_msg.removeAttribute("hidden");
      shake(must_name_msg);
    }
    else if(!all_money_valid(new_transaction_form_elements, 2)) {
      must_name_msg.setAttribute("hidden", "");
      invalid_value_msg.removeAttribute("hidden");
      shake(invalid_value_msg);
    }
    else {
      invalid_value_msg.setAttribute("hidden", "");
      must_name_msg.setAttribute("hidden", "");
      let sum = 0.0;
      let all_filled = true;
      for(let i = 2; i < new_transaction_form_elements.length; i++) {
        if(new_transaction_form_elements[i].value === "") {
          all_filled = false;
          break;
        }
        sum += +(new_transaction_form_elements[i].value);
      }
      sum = sum.toFixed(2);
      if(all_filled && sum === "0.00") {
        new_transaction_form.submit();
      }
      else {
        shake(not_zero_msg);
      }
    }
  };
};
