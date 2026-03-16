fetch("leaderboard_public.json")
.then(response => response.json())
.then(data => {

const table = document.querySelector("#leaderboard tbody");

data.forEach(row => {

const tr = document.createElement("tr");

tr.innerHTML =
`<td>${row.rank}</td>
<td>${row.team}</td>
<td>${row.score.toFixed(4)}</td>`;

table.appendChild(tr);

});

});