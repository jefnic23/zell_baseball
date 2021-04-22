var today = new Date();
var mm = String(today.getMonth() + 1).padStart(2, '0');
var dd = String(today.getDate()).padStart(2, '0');
var yyyy = today.getFullYear();
var date = `${mm}/${dd}/${yyyy}`;

var base_url = "http://statsapi.mlb.com";
var main_url = `http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date=${date}&hydrate=lineups`;

$.getJSON(main_url, function(data) {
    console.log(data);
    var games = data.dates[0].games;
    for (var i=0; i < games.length; i++) {
        if (games[i].status.detailedState != "Postponed") {
            var away_team = games[i].teams.away.team.name;
            var home_team = games[i].teams.home.team.name;
            var away_lineup = games[i].lineups.awayPlayers;
            var home_lineup = games[i].lineups.homePlayers;
            console.log(`${away_team} @ ${home_team}`);
            for (var j=0; j < away_lineup.length; j++) {
                var away_player = base_url + away_lineup[j].link;
                $.getJSON(away_player, function(data) {
                    var away_name = data.people[0].fullName;
                    var away_hand = data.people[0].batside.code;
                    console.log(`${away_name} ${away_hand}`);
                })
                var home_player = base_url + home_lineup[j].link;
                $.getJSON(home_player, function(data) {
                    var home_name = data.people[0].fullName;
                    var home_hand = data.people[0].batside.code;
                    console.log(`${home_name} ${home_hand}`);
                })
            }
        }
    }
}); 