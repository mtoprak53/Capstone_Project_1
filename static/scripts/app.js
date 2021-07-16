function submitForm(event) {
  event.preventDefault();

  // let $table = $("#food-log table");
  
  // console.log("THE TABLE IS:");
  // console.log($table);
  // console.log($("#put-rows"));

  let food = $("#food").val();
  let amount = $("#amount").val();
  let kcal_per_unit = $("#kcal_per_unit").val();
  let kcal = parseInt(kcal_per_unit) * parseInt(amount) / 100;

  let last_num = 0;

  // console.log(!!$("#put-rows tr:last td:first").text());

  if (!!$("#put-rows tr:last td:first").text()) {
    last_num = parseInt($("#put-rows tr:last td:first").text());
    // console.log(last_num);
  }

  if (last_num === 0) {
    $("#food-log").toggleClass("hidden");
  }

  const $new_row = $("<tr>")
                  .append($("<td>").addClass("rank").text(last_num + 1))
                  .append($("<td>").text(food))
                  .append($("<td>").text(amount))
                  .append($("<td>").text(kcal))
                  .append($("<td>").append($("<button>").addClass("edit").text("E")))
                  .append($("<td>").append($("<button>").addClass("delete").text("X")));

  // console.log($new_row);

  $("#put-rows").append($new_row);


  let totalAmount = $("#total-amount").text();
  totalAmount = !!totalAmount ? parseInt(totalAmount) : 0;
  console.log("typeof amount:");
  console.log(typeof amount);
  totalAmount += parseInt(amount);

  $("#total-amount").text(totalAmount);


  let totalCalories = $("#total-calories").text();
  totalCalories = !!totalCalories ? parseInt(totalCalories) : 0;
  totalCalories += kcal;

  $("#total-calories").text(totalCalories);

  console.log("totalCalories");
  console.log(totalCalories);



}

// FORM BUTTON LISTENER
$("input[type='submit']").on("click", submitForm);


function deleteRow(event) {
  event.preventDefault();
  const $row = $(event.currentTarget).parent().parent();
  const row_num = $row.eq(0).text();
  rn = parseInt(row_num);
  let count = 0;
  $row.nextAll().map(function(index) {
    $(this).children().eq(0).text(index + rn);
    count++;
  });
  $(event.currentTarget).parent().parent().remove();

  // console.log($row.nextAll());
  console.log(!!$row.nextAll("tr"));
  // console.log($row.nextAll().length);

  if (rn === 1 && count === 0) {
    $("#food-log").toggleClass("hidden");
  }
}

// DELETE BUTTON LISTENER
$('#food-log').on("click", '.delete', deleteRow);



// AMOUT ADDITION WHEN SUBMIT

// CALORIE ADDITION WHEN SUBMIT

// AMOUNT SUBTRACTION WHEN DELETE

// CALORIE SUBTRACTION WHEN DELETE

// ENTRY EDIT FUNCTIOANLITY