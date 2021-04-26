var today = new Date();
var mm = String(today.getMonth() + 1).padStart(2, '0');
var dd = String(today.getDate()).padStart(2, '0');
var yyyy = today.getFullYear();
var main_date = `${mm}/${dd}/${yyyy}`; //used in main_url
var find_date = `${yyyy}-${mm}-${dd}`; //used when getting games from main_url
document.querySelector("#date").innerHTML = `Games on ${main_date}`;

var base_url = "http://statsapi.mlb.com";
var main_url = `http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date=${main_date}&hydrate=lineups`;
var odds_url = "https://sportsbook.fanduel.com/cache/psmg/UK/60826.3.json";

function callApi(url, date) {
    return $.getJSON(url).then(data => {
        return data.dates.find(x => x.date === date);
    });
}

function getData(base, link) {
    return $.getJSON(base + link).then(data => {
        return data;
    });
}

function getFanduel(url) {
    return $.getJSON(url).then(data => {
        return data;
    });
}

function getMoneyLine(data) {
    var e = 1 + data.currentpriceup / data.currentpricedown;
    if (e >= 2) {
        var line = 100 * (e - 1);
    } else {
        var line = -100 / (e - 1);
    }
    return Math.round(line);
}

function populateTables(game) {
    if (game.status === "P" || game.status === "S") {
        //console.log(game);
        var table = document.querySelector("table > tbody");
        var row = document.createElement("tr");
        var teams = `${game.away_team} @ ${game.home_team}`;
        var game_time = game.game_time;
        var weather, over_under = "TBD", over_line = "TBD", under_line = "TBD", prediction  = "TBD";
        if (game.weather != "TBD") {
            weather = `${game.weather.condition}, ${game.weather.temp}&deg`;
        } else {
            weather = game.weather;
        }
        if (game.market) {
            over_under = game.market.currentmatchhandicap;
            over_line = getMoneyLine(game.market.selections.find(x => x.name === "Over"));
            under_line = getMoneyLine(game.market.selections.find(x => x.name === "Under"));
        }
        var items = [teams, game_time, weather, prediction, over_under, over_line, under_line];
        for (var i = 0; i < items.length; i++) {
            var td = document.createElement("td");
            if (items[i] === over_under) {
                td.setAttribute("id", `${game.market.idfoevent}`);
                td.innerHTML = items[i];
                row.appendChild(td);
            } else if (items[i] === over_line) {
                td.setAttribute("id", `${game.market.selections.find(x => x.name === "Over").idfoselection}`);
                td.innerHTML = items[i];
                row.appendChild(td);
            } else if (items[i] === under_line) {
                td.setAttribute("id", `${game.market.selections.find(x => x.name === "Under").idfoselection}`);
                td.innerHTML = items[i];
                row.appendChild(td);
            } else {
                td.innerHTML = items[i];
                row.appendChild(td);
            }
        }
        table.appendChild(row);
    }
}

function notEmpty(obj) {
    return Object.keys(obj) != 0;
}

getFanduel(odds_url).then(data => {
    //console.log(data);
    var fanduel = [];
    $.each(data.events, (i, e) => {
        var date = new Date(e.tsstart);
        if (date.getDate() == today.getDate()) {
            fanduel.push(e);
        }
    });
    callApi(main_url, find_date).then(data => {
        $.each(data.games, (i, g) => {
            //console.log(g);
            var game = {};
            var game_time = new Date(g.gameDate);
            game['game_time'] = ((game_time.getHours() + 11) % 12 + 1) + ':' + String(game_time.getMinutes()).padStart(2, '0');
            game['status'] = g.status.codedGameState;
            game['innings'] = g.scheduledInnings;
            game['venue'] = g.venue.name;
            game['weather'] = "TBD";
            game['ump'] = "TBD";
            game['away_team'] = g.teams.away.team.name;
            game['away_pitcher'] = "TBD";
            game['away_lineup'] = [];
            game['away_bullpen'] = [];
            game['home_team'] = g.teams.home.team.name;
            game['home_pitcher'] = "TBD";
            game['home_lineup'] = [];
            game['home_bullpen'] = [];
            game['market'] = null;
    
            getData(base_url, g.link).then(data => {
                //console.log(data);
                if (notEmpty(data.gameData.weather)) {
                    game['weather'] = data.gameData.weather;
                }
                if (notEmpty(data.liveData.boxscore.officials)) {
                    game["ump"] = data.liveData.boxscore.officials.find(x => x.officialType === "Home Plate");
                }
                if (notEmpty(data.gameData.probablePitchers)) {
                    if (data.gameData.probablePitchers.away) {
                        game["away_pitcher"] = data.gameData.players["ID" + data.gameData.probablePitchers.away.id];
                    }
                    if (data.gameData.probablePitchers.home) {
                        game["home_pitcher"] = data.gameData.players["ID" + data.gameData.probablePitchers.home.id];
                    }
                } 
                if (notEmpty(data.liveData.boxscore.teams.away.bullpen)) {
                    $.each(data.liveData.boxscore.teams.away.bullpen, (i, id) => {
                        game['away_bullpen'].push(data.gameData.players["ID" + id]);
                    });
                }
                if (notEmpty(data.liveData.boxscore.teams.home.bullpen)) {
                    $.each(data.liveData.boxscore.teams.home.bullpen, (i, id) => {
                        game['home_bullpen'].push(data.gameData.players["ID" + id]);
                    });
                }
                if (notEmpty(data.liveData.boxscore.teams.away.battingOrder)) {
                    $.each(data.liveData.boxscore.teams.away.battingOrder, (i, id) => {
                        game['away_lineup'].push(data.gameData.players['ID' + id]);
                    });
                }
                if (notEmpty(data.liveData.boxscore.teams.home.battingOrder)) {
                    $.each(data.liveData.boxscore.teams.home.battingOrder, (i, id) => {
                        game['home_lineup'].push(data.gameData.players['ID' + id]);
                    });
                }

                var odds = fanduel.find(x => x.participantname_away === game['away_team'] || x.participantname_home === game['home_team']);
                if (odds && odds.markets.find(x => x.idfomarkettype === 48555.1)) {
                    game_time = new Date(odds.tsstart);
                    game['game_time'] = ((game_time.getHours() + 11) % 12 + 1) + ':' + String(game_time.getMinutes()).padStart(2, '0');
                    game['market'] = odds.markets.find(x => x.idfomarkettype === 48555.1);
                }
                populateTables(game);
            });
        });
    });
});

setInterval(() => {
    getFanduel(odds_url).then(data => {
        //console.log(data);
        $.each(data.events, (i, e) => {
            if (e.markets.find(x => x.idfomarkettype === 48555.1)) {
                var market = e.markets.find(x => x.idfomarkettype === 48555.1);
                var over = market.selections.find(x => x.name === "Over");
                var under = market.selections.find(x => x.name === "Under");
                var market_ele = document.querySelector(`#${CSS.escape(market.idfoevent)}`)
                var over_ele = document.querySelector(`#${CSS.escape(over.idfoselection)}`)
                var under_ele = document.querySelector(`#${CSS.escape(under.idfoselection)}`)
                if (new Date() >= new Date(market.tsstart)) {
                    var row = market.parentNode;
                    row.parentNode.removeChild(row);
                }
                if (market_ele && market_ele.innerHTML != market.currentmatchhandicap) {
                    market_ele.innerHTML = market.currentmatchhandicap;
                }
                if (over_ele && over_ele.innerHTML != getMoneyLine(over)) {
                    over_ele.innerHTML = getMoneyLine(over);
                }
                if (under_ele && under_ele.innerHTML != getMoneyLine(under)) {
                    under_ele.innerHTML = getMoneyLine(under);
                }
            }
        });
    });
}, 30000);