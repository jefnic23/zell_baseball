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
var num_games = 0;
var num_games_test = 0;
var active_games = 0;

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
        num_games_test++;
        active_games++;
        var table = document.querySelector("#slate");
        var row = document.createElement("tr");
        var away_team_logo = logos[game.away_team_full];
        var home_team_logo = logos[game.home_team_full];
        var teams = {'away_name': game.away_team_short, "away_logo": away_team_logo, 'home_name': game.home_team_short, 'home_logo': home_team_logo};
        var weather = game.weather, over_under = "TBD", total = 'TBD', over_line = "TBD", under_line = "TBD", prediction  = "TBD";
        if (game.weather !== "TBD") {
            weather = `${game.weather.condition}, ${game.weather.temp}&deg`;
        }
        if (game.market) {
            over_under = game.market.currentmatchhandicap;
            over_line = getMoneyLine(game.market.selections.find(x => x.name === "Over"));
            under_line = getMoneyLine(game.market.selections.find(x => x.name === "Under"));
        }
        var items = [teams, game.game_time, weather, prediction, over_under, total, over_line, under_line];
        for (var i = 0; i < items.length; i++) {
            var td = document.createElement("td");
            if (items[i] === teams) {
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
            } else if (items[i] === over_under) {
                td.setAttribute("id", game.market.idfoevent); //add condition for games with no market
                td.innerHTML = items[i];
                row.appendChild(td);
            } else if (items[i] === over_line) {
                td.setAttribute("id", game.market.selections.find(x => x.name === "Over").idfoselection);
                td.innerHTML = items[i];
                row.appendChild(td);
            } else if (items[i] === under_line) {
                td.setAttribute("id", game.market.selections.find(x => x.name === "Under").idfoselection);
                td.innerHTML = items[i];
                row.appendChild(td);
            } else {
                td.innerHTML = items[i];
                row.appendChild(td);
            }
        }
        table.appendChild(row);
        // find new way to compare live games to preview games; get # of pregames from callAPI first
        if (active_games === num_games_test) {
            document.querySelector("#slate").style.visibility = "visible";
            document.querySelector(".loader").style.visibility = "hidden";
        }
    }
}

function changePrice(el, odds_type, price, market=false) {
    if (market) {
        el.innerHTML = odds_type.currentmatchhandicap;
    } else {
        el.innerHTML = getMoneyLine(odds_type);
    }
    el.classList.add(price);
    setTimeout(() => {
        el.classList.remove(price);
    }, 5500);
}

function notEmpty(obj) {
    return Object.keys(obj) != 0;
}

// main loop //

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
                /* convert to function

                if (active_games === 0) {
                    var table = document.querySelector("#slate");
                    var row = document.createElement("tr");
                    var td = document.createElement("td");
                    td.innerHTML = "No games";
                    td.colSpan = "8";
                    td.style.textAlign = "center";
                    row.appendChild(td);
                    table.appendChild(row);
                }
                */
            });
        });
    });
});

const updateOdds = setInterval(() => {
    if (num_games_test === num_games && active_games === 0) {
        // instead of clearing interval, wait until next day? try to keep this always running
        clearInterval(updateOdds);
    } else {
        getFanduel(odds_url).then(data => {
            //console.log(data);
            $.each(data.events, (i, e) => {
                if (e.markets.find(x => x.idfomarkettype === 48555.1)) {
                    var market = e.markets.find(x => x.idfomarkettype === 48555.1);
                    var over = market.selections.find(x => x.name === "Over");
                    var under = market.selections.find(x => x.name === "Under");
                    var market_el = document.querySelector(`#${CSS.escape(market.idfoevent)}`);
                    var over_el = document.querySelector(`#${CSS.escape(over.idfoselection)}`);
                    var under_el = document.querySelector(`#${CSS.escape(under.idfoselection)}`);
                    //market_el is null? late games are carrying over, add condition to skip
                    /*
                    if (new Date() >= new Date(market.tsstart)) {
                        var row = market_el.parentNode;
                        row.parentNode.removeChild(row);
                    }
                    */
                    if (market_el) {
                        if (market_el.innerHTML !== market.currentmatchhandicap) {
                            changePrice(market_el, market, "line-change", market=true);
                        }
                    }
                    if (over_el) {
                        if (over_el.innerHTML > getMoneyLine(over)) {
                            changePrice(over_el, over, "price-down");
                        } else if (over_el.innerHTML < getMoneyLine(over)) {
                            changePrice(over_el, over, "price-up");
                        }
                    } 
                    if (under_el) {
                        if (under_el.innerHTML > getMoneyLine(under)) {
                            changePrice(under_el, under, "price-down");
                        } else if (under_el.innerHTML < getMoneyLine(under)) {
                            changePrice(under_el, under, "price-up");
                        }
                    } 
                }
            });
        });
    }
}, 30000);