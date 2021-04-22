var today = new Date();
var mm = String(today.getMonth() + 1).padStart(2, '0');
var dd = String(today.getDate()).padStart(2, '0');
var yyyy = today.getFullYear();
var date = `${mm}/${dd}/${yyyy}`;

var base_url = "http://statsapi.mlb.com";
var main_url = `http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date=${date}&hydrate=lineups`;

var game_list = [];

$.getJSON(main_url, function(result) {
    //console.log(result);
    $.each(result.dates[0].games, function(i, data) {
        //console.log(data);
        var game = {};
        if (data.status.detailedState != "Postponed") {
            var away_team = data.teams.away.team.name;
            var home_team = data.teams.home.team.name;
            game['away_team'] = away_team;
            game['away_lineup'] = [];
            game['away_pitcher'] = "TBD";
            game['home_team'] = home_team;
            game['home_lineup'] = [];
            game['home_pitcher'] = "TBD";
            game['scheduled_innings'] = data.scheduledInnings;
            game['ump'] = "";

            var live_feed = base_url + data.link;
            $.getJSON(live_feed, function(data) {
                //console.log(data);
                game['game_time'] = data.gameData.datetime.time;
                game['venue'] = data.gameData.venue;
                game['weather'] = data.gameData.weather;

                var pitchers = data.gameData.probablePitchers;
                if (pitchers) {
                    var away_pitcher = {};
                    away_pitcher['name'] = pitchers.away.fullName;

                    var home_pitcher = {};
                    home_pitcher['name'] = pitchers.home.fullName;

                    var away_link = base_url + pitchers.away.link;
                    $.getJSON(away_link, function(data) {
                        away_pitcher['hand'] = data.people[0].pitchHand.code;
                    });

                    var home_link = base_url + pitchers.away.link;
                    $.getJSON(home_link, function(data) {
                        home_pitcher['hand'] = data.people[0].pitchHand.code;
                    });

                    game['away_pitcher'] = away_pitcher;
                    game['home_pitcher'] = home_pitcher;
                }

                var umps = data.liveData.boxscore.officials;
                var ump = {};
                $.each(umps, function(i, data) {
                    if (data.officialType == "Home Plate") {
                        ump['name'] = data.official.fullName;

                        var ump_link = base_url + data.official.link;
                        $.getJSON(ump_link, function(data) {
                            ump['sz_bottom'] = data.people[0].strikeZoneBottom;
                            ump['sz_top'] = data.people[0].strikeZoneTop;
                        });
                    }
                });

                game['ump'] = ump;
            });

            var lineups = data.lineups;
            if (lineups) {
                if (lineups.awayPlayers) {
                    var away_lineup = lineups.awayPlayers;
                    for (var j=0; j < away_lineup.length; j++) {
                        var away_player = base_url + away_lineup[j].link;
                        $.getJSON(away_player, function(result) {
                            $.each(result.people, function(i, data) {
                                var player = {};
                                var name = data.fullName;
                                var hand = data.batSide.code;
                                player['name'] = name;
                                player['hand'] = hand;
                                game['away_lineup'].push(player);
                            });
                        });
                    }
                }
                if (lineups.homePlayers) {
                    var home_lineup = lineups.homePlayers;
                    for (var j=0; j < lineups.homePlayers.length; j++) {
                        var home_player = base_url + home_lineup[j].link;
                        $.getJSON(home_player, function(result) {
                            $.each(result.people, function(i, data) {
                                var player = {};
                                var name = data.fullName;
                                var hand = data.batSide.code;
                                player['name'] = name;
                                player['hand'] = hand;
                                game['home_lineup'].push(player);
                            });
                        });
                    }
                }
            }
        }
        game_list.push(game);
    });
}); 

console.log(game_list);

const settings = {
	"async": true,
	"crossDomain": true,
	"url": "https://sports-odds-betapi.p.rapidapi.com/v1/sports/line/en",
	"method": "GET",
	"headers": {
		"package": "4a788ec11cd42226e2fdcbd62253379c",
		"x-rapidapi-key": "fd80fc833bmsh2b174af060c335fp1e8ec1jsneefa0b5408b1",
		"x-rapidapi-host": "sports-odds-betapi.p.rapidapi.com"
	}
};

$.ajax(settings).done(function (response) {
	console.log(response);
});