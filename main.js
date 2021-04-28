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
var logo_url = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams";
var num_games = 0;
var num_games_test = 0;
var active_games = 0;

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

// call once to get logos, then in populate function search the result
function getLogos(url) {
    return $.getJSON(url).then(data => {
        return data;
    });
}

function teamLogo(logos, tname) {
    console.log(logos.find(x => x.team.displayName === tname).logos[2]);
    return logos.find(x => x.team.displayName === tname).logos[2];
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
        num_games_test++;
        active_games++;
        var table = document.querySelector("#slate");
        var row = document.createElement("tr");
        var away_team_name = game.away_team_short;
        try {
            var away_team_logo = teamLogo(logos, game.away_team_full);
        }
        catch(error) {
            var away_team_logo = null;
        }
        try {
            var home_team_logo = teamLogo(logos, game.home_team_full);
        }
        catch(error) {
            var home_team_logo = null;
        }
        var home_team_name = game.home_team_short;
        var teams = {'away_name': away_team_name, "away_logo": away_team_logo, 'home_name': home_team_name, 'home_logo': home_team_logo};
        var game_time = game.game_time;
        var weather = game.weather, over_under = "TBD", over_line = "TBD", under_line = "TBD", prediction  = "TBD";
        if (game.weather !== "TBD") {
            weather = `${game.weather.condition}, ${game.weather.temp}&deg`;
        }
        if (game.market) {
            over_under = game.market.currentmatchhandicap;
            over_line = getMoneyLine(game.market.selections.find(x => x.name === "Over"));
            under_line = getMoneyLine(game.market.selections.find(x => x.name === "Under"));
        }
        var items = [teams, game_time, weather, prediction, over_under, over_line, under_line];
        for (var i = 0; i < items.length; i++) {
            var td = document.createElement("td");
            if (items[i] === teams) {
                var away_span = document.createElement('span');
                var home_span = document.createElement('span');
                away_span.innerHTML = `${teams.away_name} @ `;
                away_span.style.backgroundColor = `url(${teams.away_logo});`;
                home_span.innerHTML = teams.home_name;
                home_span.style.backgroundImage = `url(${teams.home_logo});`;
                td.appendChild(away_span);
                td.appendChild(home_span);
                row.appendChild(td);
            } else if (items[i] === over_under) {
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
        // find new way to compare live games to preview games
        if (active_games === num_games_test) {
            document.querySelector("#slate").style.visibility = "visible";
            document.querySelector(".loader").style.visibility = "hidden";
        }
    }
}

function notEmpty(obj) {
    return Object.keys(obj) != 0;
}

// need new source of logos; just download them?
var logos = []
getLogos(logo_url).then(data => {
    //console.log(data);
    $.each(data.sports[0].leagues[0].teams, (i, t) => {
        logos.push(t);
    }); 
});

// get logos somewhere here instead of above; are there missing logos?
getFanduel(odds_url).then(data => {
    //console.log(data);
    var fanduel = [];
    $.each(data.events, (i, e) => {
        var date = new Date(e.tsstart);
        if (date.getDate() === today.getDate()) {
            fanduel.push(e);
        }
    });
    callApi(main_url, find_date).then(data => {
        //console.log(data);
        num_games = data.totalGames;
        $.each(data.games, (i, g) => {
            //console.log(g);
            var game = {};
            game["game_time"] = new Date(g.gameDate).toLocaleString('en-US', {hour: 'numeric', minute: 'numeric', hour12: true});
            game['status'] = g.status.codedGameState;
            game['innings'] = g.scheduledInnings;
            game['venue'] = g.venue.name;
            game['weather'] = "TBD";
            game['ump'] = "TBD";
            game['away_team_full'] = g.teams.away.team.name;
            game['away_pitcher'] = "TBD";
            game['away_lineup'] = [];
            game['away_bullpen'] = [];
            game['home_team_full'] = g.teams.home.team.name;
            game['home_pitcher'] = "TBD";
            game['home_lineup'] = [];
            game['home_bullpen'] = [];
            game['market'] = null;
    
            getData(base_url, g.link).then(d => {
                //console.log(d);
                game['away_team_short'] = d.gameData.teams.away.teamName;
                game['home_team_short'] = d.gameData.teams.home.teamName;
                if (notEmpty(d.gameData.weather)) {
                    game['weather'] = d.gameData.weather;
                }
                if (notEmpty(d.liveData.boxscore.officials)) {
                    game["ump"] = d.liveData.boxscore.officials.find(x => x.officialType === "Home Plate");
                }
                if (notEmpty(d.gameData.probablePitchers)) {
                    if (d.gameData.probablePitchers.away) {
                        game["away_pitcher"] = d.gameData.players["ID" + d.gameData.probablePitchers.away.id];
                    }
                    if (d.gameData.probablePitchers.home) {
                        game["home_pitcher"] = d.gameData.players["ID" + d.gameData.probablePitchers.home.id];
                    }
                } 
                if (notEmpty(d.liveData.boxscore.teams.away.bullpen)) {
                    $.each(d.liveData.boxscore.teams.away.bullpen, (i, id) => {
                        game['away_bullpen'].push(d.gameData.players["ID" + id]);
                    });
                }
                if (notEmpty(d.liveData.boxscore.teams.home.bullpen)) {
                    $.each(d.liveData.boxscore.teams.home.bullpen, (i, id) => {
                        game['home_bullpen'].push(d.gameData.players["ID" + id]);
                    });
                }
                if (notEmpty(d.liveData.boxscore.teams.away.battingOrder)) {
                    $.each(d.liveData.boxscore.teams.away.battingOrder, (i, id) => {
                        game['away_lineup'].push(d.gameData.players['ID' + id]);
                    });
                }
                if (notEmpty(d.liveData.boxscore.teams.home.battingOrder)) {
                    $.each(d.liveData.boxscore.teams.home.battingOrder, (i, id) => {
                        game['home_lineup'].push(d.gameData.players['ID' + id]);
                    });
                }
                var odds = fanduel.find(x => x.participantname_away === game['away_team_full'] || x.participantname_home === game['home_team_full']);
                if (odds && odds.markets.find(x => x.idfomarkettype === 48555.1)) {
                    game['game_time'] = new Date(odds.tsstart).toLocaleString('en-US', {hour: 'numeric', minute: 'numeric', hour12: true});
                    game['market'] = odds.markets.find(x => x.idfomarkettype === 48555.1);
                }
                populateTables(game);
                //convert to function
                if (num_games_test === num_games && active_games === 0) {
                    var table = document.querySelector("#slate");
                    var row = document.createElement("tr");
                    var td = document.createElement("td");
                    td.innerHTML = "No games";
                    td.colSpan = "7";
                    td.style.textAlign = "center";
                    row.appendChild(td);
                    table.appendChild(row);
                }
            });
        });
    });
});

const updateOdds = setInterval(() => {
    if (num_games_test === num_games && active_games === 0) {
        //console.log('no update');
        clearInterval(updateOdds);
    } else {
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
                        var row = market_ele.parentNode; //market_ele is null? maybe late games are carrying over
                        row.parentNode.removeChild(row);
                    }
                    // write functions to simplify the code below
                    if (market_ele) {
                        if (market_ele.innerHTML > market.currentmatchhandicap) {
                            market_ele.innerHTML = market.currentmatchhandicap;
                            market_ele.classList.add("price-up");
                            setTimeout(() => {
                                market_ele.classList.remove("price-up");
                            }, 5500);
                        } else if (market_ele.innerHTML < market.currentmatchhandicap) {
                            market_ele.innerHTML = market.currentmatchhandicap;
                            market_ele.classList.add("price-down");
                            setTimeout(() => {
                                market_ele.classList.remove("price-down");
                            }, 5500);
                        }
                    }
                    if (over_ele) {
                        if (over_ele.innerHTML > getMoneyLine(over)) {
                            over_ele.innerHTML = getMoneyLine(over);
                            over_ele.classList.add("price-up");
                            setTimeout(() => {
                                over_ele.classList.remove("price-up");
                            }, 5500);
                        } else if (over_ele.innerHTML < getMoneyLine(over)) {
                            over_ele.innerHTML = getMoneyLine(over);
                            over_ele.classList.add("price-down");
                            setTimeout(() => {
                                over_ele.classList.remove("price-down");
                            }, 5500);
                        }
                    } 
                    if (under_ele) {
                        if (under_ele.innerHTML > getMoneyLine(under)) {
                            under_ele.innerHTML = getMoneyLine(under);
                            under_ele.classList.add("price-up");
                            setTimeout(() => {
                                under_ele.classList.remove("price-up");
                            }, 5500);
                        } else if (under_ele.innerHTML < getMoneyLine(under)) {
                            under_ele.innerHTML = getMoneyLine(under);
                            under_ele.classList.add("price-down");
                            setTimeout(() => {
                                under_ele.classList.remove("price-down");
                            }, 5500);
                        }
                    } 
                }
            });
        });
    }
}, 30000);