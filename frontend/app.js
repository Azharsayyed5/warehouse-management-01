function myFunction() {
    document.getElementById("demo").innerHTML = "Hello World";
    }

function formatParams( params ){
    return "?" + Object
            .keys(params)
            .map(function(key){
            return key+"="+encodeURIComponent(params[key])
            })
            .join("&")
    }

function sendData(order){
    $sort_by = "timestamp"
    if(document.getElementById('timestamp').checked) {
        $sort_by = "timestamp"
      }else if(document.getElementById('quantity').checked) {
        $sort_by = "quantity"
      }
    
    var params = {
        sort: order, 
        field: $sort_by,
    }
    location.href = "/report" + formatParams(params);
}

function searchFunction() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[0];
      td2 = tr[i].getElementsByTagName("td")[1];
      td3 = tr[i].getElementsByTagName("td")[2];
      if (td) {
        txtValue = td.textContent || td.innerText;
        console.log(txtValue, td.textContent, td.innerText)
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
         txtValue = td2.textContent || td2.innerText;
          if (txtValue.toUpperCase().indexOf(filter) > -1) {
         tr[i].style.display = "";
          } else {
            txtValue = td3.textContent || td3.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
          }
        }
      }      
    }
   }
}