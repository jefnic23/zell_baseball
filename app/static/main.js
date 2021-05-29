var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
var today = new Date();
var mm = String(today.getMonth() + 1).padStart(2, '0');
var dd = String(today.getDate()).padStart(2, '0');
var yyyy = today.getFullYear();
var main_date = `${mm}/${dd}/${yyyy}`; // used in main_url
var find_date = `${yyyy}-${mm}-${dd}`; // used when getting games from main_url
var base_url = "https://statsapi.mlb.com";
var main_url = `https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date=${main_date}&hydrate=lineups`;
var odds_url = "https://sportsbook.fanduel.com/cache/psmg/UK/60826.3.json";
var num_games = 0; // set this from callapi on dom load
var active_games = 0; // set this from callapi on dom load
var live_games = 0;
var no_games = false;
const logos = {'Los Angeles Angels': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/108.svg',
    'Arizona Diamondbacks': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/109.svg',
    'Baltimore Orioles': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/110.svg',
    'Boston Red Sox': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/111.svg',
    'Chicago Cubs': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/112.svg',
    'Cincinnati Reds': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/113.svg',
    'Cleveland Indians': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/114.svg',
    'Colorado Rockies': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/115.svg',
    'Detroit Tigers': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/116.svg',
    'Houston Astros': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/117.svg',
    'Kansas City Royals': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/118.svg',
    'Los Angeles Dodgers': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/119.svg',
    'Washington Nationals': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/120.svg',
    'New York Mets': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/121.svg',
    'Oakland Athletics': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/133.svg',
    'Pittsburgh Pirates': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/134.svg',
    'San Diego Padres': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/135.svg',
    'Seattle Mariners': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/136.svg',
    'San Francisco Giants': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/137.svg',
    'St. Louis Cardinals': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/138.svg',
    'Tampa Bay Rays': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/139.svg',
    'Texas Rangers': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/140.svg',
    'Toronto Blue Jays': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/141.svg',
    'Minnesota Twins': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/142.svg',
    'Philadelphia Phillies': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/143.svg',
    'Atlanta Braves': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/144.svg',
    'Chicago White Sox': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/145.svg',
    'Miami Marlins': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/146.svg',
    'New York Yankees': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/147.svg',
    'Milwaukee Brewers': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/158.svg'
}

function sendData(game) {
    socket.emit('game', {'game': game});
}

function changeLine(over_under, prediction, over, under, ids) {
    socket.emit('changeLine', {'over_under': over_under, 'prediction': prediction, 'over': over, 'under': under, 'ids': ids});
}

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

function changeClass(el, _class) {
    el.classList.add(_class);
    setTimeout(() => {
        el.classList.remove(_class);
    }, 5500);
}

function populateTables(data) {
    // console.log(data);
    var game = data.game;
    var table = document.querySelector("#slate");
    var row = document.createElement("tr");
    var away_team_logo = logos[game.away_team_full];
    var home_team_logo = logos[game.home_team_full];
    var teams = {'away_name': game.away_team_short, "away_logo": away_team_logo, 'home_name': game.home_team_short, 'home_logo': home_team_logo};
    var game_time = new Date(game.game_time).toLocaleString('en-US', {hour: 'numeric', minute: 'numeric', hour12: true});
    var prediction = data.prediction;
    var adj_line = data.adj_line;
    var total = data.total;
    var bet = data.bet;
    var weather = game.weather;
    var over_under = game.over_under;
    if (weather !== "TBD") {
        if (weather.condition === "Drizzle" || weather.condition === "Rain" || weather.condition === "Snow") {
            row.style.border = "3px solid #dc3545";
        }
        if (game.venue === "Wrigley Field" && data.direction === "In" && data.speed >= 10) {
            row.style.border = "3px solid #dc3545";
        }
    }
    if (prediction === "TBD") {
        row.classList.add('grayout');
    }
    var items = [teams, game_time, prediction, over_under, adj_line, total, bet];
    for (var i = 0; i < items.length; i++) {
        var td = document.createElement("td");
        if (i === 0) {
            var div = document.createElement("div");
            var away_div = document.createElement("div");
            var away_name_div = document.createElement("div");
            var away_logo_div = document.createElement("div");
            var away_logo_img = document.createElement("img");
            away_name_div.innerHTML = teams.away_name;
            away_logo_img.setAttribute("src", teams.away_logo);
            away_logo_img.classList.add("logo");
            away_logo_div.appendChild(away_logo_img);
            away_div.appendChild(away_logo_div);
            away_div.appendChild(away_name_div);

            var at_span = document.createElement("span");
            at_span.innerHTML = " @ ";

            var home_div = document.createElement("div");
            var home_name_div = document.createElement("div");
            var home_logo_div = document.createElement("div");
            var home_logo_img = document.createElement("img");
            home_name_div.innerHTML = teams.home_name;
            home_logo_img.setAttribute("src", teams.home_logo);
            home_logo_img.classList.add("logo");
            home_logo_div.appendChild(home_logo_img);
            home_div.appendChild(home_logo_div);
            home_div.appendChild(home_name_div);
            
            td.style.height = "0";
            div.style.height = "100%";
            div.classList.add("teams");
            div.appendChild(away_div);
            div.appendChild(at_span);
            div.appendChild(home_div);
            td.appendChild(div);
            row.appendChild(td);
        } 
        if (i === 1 || i === 2) {
            td.innerHTML = items[i];
            row.appendChild(td);
        }
        if (i === 3) {
            // add condition for games with no market, or stop them from getting passed here
            td.setAttribute("id", game.market.idfoevent);
            td.innerHTML = items[i];
            row.appendChild(td);
        }
        if (i === 4) {
            td.setAttribute("id", game.market.idfomarket);
            td.innerHTML = items[i];
            row.appendChild(td);
        }
        if (i === 5) {
            td.innerHTML = items[i];
            var over_el = game.market.selections.find(x => x.name === "Over");
            td.setAttribute('id', over_el.idfoselection);
            row.appendChild(td);
        }
        if (i === 6) {
            td.innerHTML = items[i];
            td.setAttribute('id', data.gamePk);
            if (bet !== "TBD" && bet !== "No Value") {
                if (prediction > over_under && total >= 1.1) {
                    td.innerHTML = `${items[i]}`
                    td.classList.add("betover");
                } 
                if (over_under > prediction && total <= -1.1) {
                    td.innerHTML = `${items[i]}`
                    td.classList.add("betunder");
                }
            }
            row.appendChild(td);
        }
    }
    table.appendChild(row);
}

function changePrice(el_id, odds_type) {
    var el = document.querySelector(`#${CSS.escape(el_id)}`);
    if (el.innerHTML > odds_type) {
        el.innerHTML = odds_type;
        changeClass(el, 'price-down');
    }
    if (el.innerHTML < odds_type) {
        el.innerHTML = odds_type;
        changeClass(el, 'price-up');
    }
}

function changeValue(el_id, value, total) {
    var el = document.querySelector(`#${CSS.escape(el_id)}`);
    if (el.innerHTML > value) {
        el.innerHTML = value;
        changeClass(el, 'bet-down');
    }
    if (el.innerHTML < value) {
        el.innerHTML = value;
        changeClass(el, 'bet-up');
    }
    if (el.innerHTML === 'No Value' && total >= 0.5) {
        el.innerHTML = value;
        el.classList.add("betover");
    }
    if (el.innerHTML === 'No Value' && total <= -0.5) {
        el.innerHTML = value;
        el.classList.add("betunder");
    }
    if (el.innerHTML != 'No Value' && total <= 0.5 && total >= -0.5) {
        el.innerHTML = 'No Value';
        el.setAttribute('class', '');
    }
}

function noGames() {
    var table = document.querySelector("#slate");
    var row = document.createElement("tr");
    var td = document.createElement("td");
    td.innerHTML = "No games";
    td.colSpan = "7";
    td.style.textAlign = "center";
    row.appendChild(td);
    table.appendChild(row);
    no_games = true;
}

function notEmpty(obj) {
    return Object.keys(obj) != 0;
}

// main loop //

document.querySelector("#date").innerHTML = `Games on ${main_date}`;

getFanduel(odds_url).then(data => {
    // console.log(data);
    bet_games = data.events.length;
    var fanduel = [];
    $.each(data.events, (i, e) => {
        var date = new Date(e.tsstart);
        if (date.getDate() === today.getDate()) {
            fanduel.push(e);
        }
    });
    callApi(main_url, find_date).then(data => {
        active_games = data.games.filter(x => x.status.codedGameState === "P" || x.status.codedGameState === "S" ).length;
        num_games = data.totalGames;
        if (active_games === 0) {
            noGames();
            document.querySelector("#slate").style.visibility = "visible";
            document.querySelector(".loader").style.visibility = "hidden";
        }
        $.each(data.games, (i, g) => {
            // console.log(g);
            if (g.status.codedGameState === "P" || g.status.codedGameState === "S") {
                var game = {};
                game['gamePk'] = g.gamePk;
                game["game_time"] = new Date(g.gameDate);
                game['status'] = g.status.codedGameState;
                game['double_header'] = g.doubleHeader;
                game['game_number'] = g.gameNumber;
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
                game['over_under'] = null;
                game['over_line'] = null;
                game['under_line'] = null;
        
                getData(base_url, g.link).then(d => {
                    // console.log(d);
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
                    try {
                        var odds = fanduel.filter(x => x.participantname_away === game['away_team_full'] || x.participantname_home === game['home_team_full']);
                        // console.log(odds);
                        if (game['game_number'] === 1) {
                            game['game_time'] = new Date(odds[0].tsstart);
                            game['market'] = odds[0].markets.find(x => x.idfomarkettype === 48555.1);
                            game['over_under'] = game.market.currentmatchhandicap;
                            game['over_line'] = getMoneyLine(game.market.selections.find(x => x.name === "Over"));
                            game['under_line'] = getMoneyLine(game.market.selections.find(x => x.name === "Under"));
                        } else {
                            game['game_time'] = new Date(odds[1].tsstart);
                            game['market'] = odds[1].markets.find(x => x.idfomarkettype === 48555.1);
                            game['over_under'] = game.market.currentmatchhandicap;
                            game['over_line'] = getMoneyLine(game.market.selections.find(x => x.name === "Over"));
                            game['under_line'] = getMoneyLine(game.market.selections.find(x => x.name === "Under"));
                        }
                        sendData(game);
                        live_games++;
                    }
                    catch (error) {}
                });
            }
        });
    });
});

var games = [];
var pks = [];
socket.on("predictionData", data => {
    // console.log(data);
    games.push(data);
    if (games.length === live_games) {
        games.sort((a, b) => (a.game_time.localeCompare(b.game_time)));
        $.each(games, (i, g) => {
            // console.log(g);
            if (!pks.includes(g.gamePk)) {
                populateTables(g);
                pks.push(g.gamePk);
            }
        });
        document.querySelector("#slate").style.visibility = "visible";
        document.querySelector(".loader").style.visibility = "hidden";
    }
});

socket.on("lineChange", data => {
    // console.log(data);
    changePrice(data.ids.actual_id, data.over_under);
    changePrice(data.ids.adj_id, data.adj_line);
    changePrice(data.ids.total_id, data.new_total);
    changeValue(data.ids.value_id, data.bet, data.new_total);
});

function updateOdds() {
    if (!no_games) {
        if (active_games === 0) {
            noGames();
        }
        getFanduel(odds_url).then(data => {
            $.each(data.events, (i, e) => {
                // console.log(e);
                if (games.find(x => x.game.market.idfoevent === e.idfoevent)) {
                    var game = games.find(x => x.game.market.idfoevent === e.idfoevent);
                    var market = e.markets.find(x => x.idfomarkettype === 48555.1);
                    var over = getMoneyLine(market.selections.find(x => x.name === "Over"));
                    var under = getMoneyLine(market.selections.find(x => x.name === "Under"));
                    var ids = {"actual_id": market.idfoevent, "adj_id": market.idfomarket, "total_id": market.selections.find(x => x.name === "Over").idfoselection, "value_id": game.gamePk};
                    var now = new Date();
                    var game_time = new Date(market.tsstart);
                    if (now.getTime() >= game_time.getTime()) {
                        $(document.querySelector(`#${CSS.escape(game.gamePk)}`)).closest('tr').remove();
                        active_games--;
                    } 
                    changeLine(market.currentmatchhandicap, game.prediction, over, under, ids);
                }
            });
        });
    } 
}

(function mainLoop() {
    let rand = Math.floor(Math.random() * 10) + 10;
    setTimeout(() => {
        updateOdds();
        mainLoop();
    }, rand * 1000);
}());

/*

$.getJSON("http://statsapi.mlb.com/api/v1/people/605113/stats?stats=career&group=fielding").then(data => {
    console.log(data);
});

*/