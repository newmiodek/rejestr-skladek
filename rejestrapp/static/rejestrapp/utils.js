function is_money_valid(ex_a) {
  let ex = ex_a.replace(/,/g, ".");
  return /^-?[1-9][0-9]*(\.[0-9]{1,2})?$/.test(ex) || /^-?0(\.[0-9]{1,2})?$/.test(ex)
}

function all_money_valid(els, from) {
  for(let i = from; i < els.length; i++) {
    if(!is_money_valid(els[i].value)) {
      return false;
    }
  }
  return true;
}

async function shake(el) {
  el.style["animation"] = "shake 0.5s";
  await new Promise(_ => setTimeout(_, 500));
  el.style["animation"] = "";
}

function get_form_stuff() {
  const new_transaction_form = document.getElementById("new_transaction_form");
  const new_transaction_form_elements = new_transaction_form.getElementsByTagName("input");
  const must_name_msg = document.getElementById("must_name_new_transaction")
  const invalid_value_msg = document.getElementById("invalid_value");
  return [new_transaction_form, new_transaction_form_elements, must_name_msg, invalid_value_msg];
}
