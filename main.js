var today = new Date();
var mm = String(today.getMonth() + 1).padStart(2, '0');
var dd = String(today.getDate()).padStart(2, '0');
var yyyy = today.getFullYear();
var date = `${mm}/${dd}/${yyyy}`;
document.querySelector("#slate").innerHTML = `Games on ${date}`;

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

            var game_time = new Date(data.gameDate);
            game['game_time'] = ((game_time.getHours() + 11) % 12 + 1) + ':' + String(game_time.getMinutes()).padStart(2, '0');

            var live_feed = base_url + data.link;
            $.getJSON(live_feed, function(data) {
                //console.log(data);
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

                /*
                var bullpens = data.liveData.boxscore.teams;
                var away_ids = bullpens.away.bullpen;
                var home_ids = bullpens.home.bullpen;
                console.log(bullpens);
                for (var i = 0; i < data.players.length; i++) {
                    for (var j = 0; j < away_ids.length; j++) {
                        if (data.players[i].id == away_ids[j]) {
                            away_ids[j] = data.players[i].fullName;
                        }
                    }
                    for (var j = 0; j < home_ids.length; j++) {
                        if (data.players[i].id == home_ids[j]) {
                            home_ids[j] = data.players[i].fullName;
                        }
                    }
                }
                game['away_bullpen'] = away_ids;
                game['home_bullpen'] = home_ids;
                */

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

function getMoneyLine(data) {
    var e = 1 + data.currentpriceup / data.currentpricedown;
    if (e >= 2) {
        var line = 100 * (e - 1);
    } else {
        var line = -100 / (e - 1);
    }
    return Math.round(line);
}

var fanduel = "https://sportsbook.fanduel.com/cache/psmg/UK/60826.3.json";
$.getJSON(fanduel, function(results) {
    //console.log(results);
    $.each(results.events, function(i, data) {
        //console.log(data)
        var away_team = data.participantname_away;
        var home_team = data.participantname_home;
        var runs_market = data.markets.find(x => x.name === "Total Runs");
        var over_under = runs_market.currentmatchhandicap;
        var over = runs_market.selections.find(x => x.name === "Over");
        var under = runs_market.selections.find(x => x.name === "Under");
        var over_line = getMoneyLine(over);
        var under_line = getMoneyLine(under);

        let obj = game_list.find(x => x.away_team === away_team);
        obj['over_under'] = over_under
        obj['over_line'] = over_line;
        obj['under_line'] = under_line;
    });
});

//console.log(game_list);

var container = document.querySelector("#table-container");

function populateTables() {
    $.each(game_list, function(i, game) {
        //console.log(game);
        var table = document.createElement("table");
        container.appendChild(table);
        var header = document.createElement("tr");
        var row = document.createElement("tr");
        var titles = ["Teams", "Game Time", "Condition", "Temp", "Actual Line", "Over", "Under"];
        var teams = `${game.away_team} @ ${game.home_team}`;
        var game_time = game.game_time;
        var condition = game.weather.condition;
        var temp = game.weather.temp + "&deg";
        var over_under = game.over_under;
        var over_line = game.over_line;
        var under_line = game.under_line; 
        var items = [teams, game_time, condition, temp, over_under, over_line, under_line];
        for (var j = 0; j < titles.length; j++) {
            var th = document.createElement("th");
            th.innerHTML = titles[j];
            header.appendChild(th);
    
            var td = document.createElement("td");
            td.innerHTML = items[j];
            row.appendChild(td);
        }
        table.appendChild(header);
        table.appendChild(row);
    });
}

setTimeout(populateTables, 3000);


//backup options for odds data

/*
var odds_url = "https://api.lineups.com/mlb/fetch/live_odds";
$.getJSON(odds_url, function(results) {
    //console.log(results.results);
    $.each(results.results, function(i, data) {
        var away_team = data.away.team_name;
        var away_bets = data.away.bets.filter(function(ele) {
            if (ele.bookmaker_name == "FanDuel" && ele.bet_type == "over") {
                return ele;
            } 
        });
        var over_odds = away_bets[0].over_current_odds;
        var home_bets = data.home.bets.filter(function(ele) {
            if (ele.bookmaker_name == "FanDuel" && ele.bet_type == "under") {
                return ele;
            } 
        });
        var under_odds = home_bets[0].under_current_odds;

        var over_current = away_bets[0].over_current;
        var under_current = home_bets[0].under_current;

        let obj = game_list.find(x => x.away_team == away_team);
        if (over_current) {
            obj['over_under'] = over_current;
        } else if (under_current) {
            obj['over_under'] = under_current;
        }
        obj['over_odds'] = over_odds;
        obj['under_odds'] = under_odds;
    });
});

var espn = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard";
$.getJSON(espn, function(result) {
    console.log(result);
});
*/