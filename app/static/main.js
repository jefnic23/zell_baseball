const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
const table = document.querySelector("#slate");
const logos = {
    'Los Angeles Angels': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/108.svg',
    'Arizona Diamondbacks': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/109.svg',
    'Baltimore Orioles': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/110.svg',
    'Boston Red Sox': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/111.svg',
    'Chicago Cubs': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/112.svg',
    'Cincinnati Reds': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/113.svg',
    'Cleveland Guardians': 'https://www.mlbstatic.com/team-logos/team-cap-on-light/114.svg',
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

// async function getFanduel(url="https://sportsbook.fanduel.com/cache/psmg/UK/60826.3.json") {
//     const res = await fetch(url);
//     return await res.json();
// }

function createTeams(row, away_name, away_logo, home_name, home_logo) {
    let td = document.createElement("td");
    let div = document.createElement("div");
    let away_div = document.createElement("div");
    let away_name_div = document.createElement("div");
    let away_logo_div = document.createElement("div");
    let away_logo_img = document.createElement("img");
    away_name_div.innerHTML = away_name;
    away_logo_img.setAttribute("src", away_logo);
    away_logo_img.classList.add("logo");
    away_logo_div.appendChild(away_logo_img);
    away_div.appendChild(away_logo_div);
    away_div.appendChild(away_name_div);

    let at_span = document.createElement("span");
    at_span.innerHTML = " @ ";

    let home_div = document.createElement("div");
    let home_name_div = document.createElement("div");
    let home_logo_div = document.createElement("div");
    let home_logo_img = document.createElement("img");
    home_name_div.innerHTML = home_name;
    home_logo_img.setAttribute("src", home_logo);
    home_logo_img.classList.add("logo");
    home_logo_div.appendChild(home_logo_img);
    home_div.appendChild(home_logo_div);
    home_div.appendChild(home_name_div);
    
    div.style.height = "100%";
    div.classList.add("teams");
    div.appendChild(away_div);
    div.appendChild(at_span);
    div.appendChild(home_div);
    td.appendChild(div);
    return row.appendChild(td);
}

function createGameTime(row, game_time) {
    let td = document.createElement("td");
    td.innerHTML = game_time;
    return row.appendChild(td);
}

function createPrediction(row, prediction, predData, pred_name, home_team, ump) {
    let td = document.createElement("td");
    let pred_div = document.createElement("div");
    pred_div.innerHTML = prediction;
    pred_div.classList.add('tooltip');
    td.appendChild(pred_div);
    td.classList.add("tooltip-container");
    if (prediction !== "TBD") {
        let span = document.createElement('span');
        span.classList.add('tooltiptext');
        let ul = document.createElement('ul');
        let pred_data = [
            predData.park_factor,
            predData.wind_factor,
            `${predData.temp_factor} (N/A)`,
            `${predData.ump_factor} (${ump.official.fullName})`,
            predData.away_fielding,
            predData.home_fielding,
            predData.home_matchups,
            predData.away_matchups,
            predData.handicap
        ];
        for (let j = 0; j < pred_data.length; j++) {
            if (pred_name[j] === 'Wind' && home_team !== 'Chicago Cubs') { continue; }
            let li = document.createElement('li');
            li.innerHTML = `<strong>${pred_name[j]}</strong>: ${pred_data[j]}`;
            ul.appendChild(li);
        }
        span.appendChild(ul);
        pred_div.appendChild(span);
    }
    return row.appendChild(td);
}

function createLines(row, idfoevent, over_under, over_line, under_line) {
    let td = document.createElement("td");
    let div = document.createElement("div");
    let line_div = document.createElement("div");
    let ou_div = document.createElement("div");
    let over_div = document.createElement("div");
    let under_div = document.createElement("div");
    line_div.setAttribute("id", idfoevent);
    line_div.innerHTML = over_under;
    over_div.innerHTML = `${over_line} O`;
    under_div.innerHTML = `${under_line} U`;
    div.style.height = "100%";
    div.classList.add('lines');
    ou_div.appendChild(over_div);
    ou_div.appendChild(under_div);
    div.appendChild(line_div);
    div.appendChild(ou_div);
    td.appendChild(div);
    return row.appendChild(td);
}

function createTotal(row, total, market, thresholds, prediction, over_under, over_threshold, under_threshold) {
    let td = document.createElement("td");
    let total_div = document.createElement("div");
    total_div.innerHTML = total;
    total_div.classList.add('tooltip');
    td.appendChild(total_div);
    td.classList.add("tooltip-container");
    td.setAttribute('id', market);
    if (total !== "TBD") {
        let span = document.createElement('span');
        span.classList.add('tooltiptext');
        span.style.padding = "13px";
        let tbl = document.createElement('div');
        tbl.classList.add('table');
        for (let j = 0; j < thresholds.length; j++) {
            let tr = document.createElement('div');
            tr.classList.add('table-row');
            for (let i = 0; i < thresholds[j].length; i++){
                let tc = document.createElement('div');
                tc.classList.add('table-cell');
                tc.innerHTML = thresholds[j][i];
                tr.appendChild(tc);
            }
            tbl.appendChild(tr);
        }

        if (prediction > over_under && total > over_threshold) {
            td.classList.add("betover");
        } 
        if (over_under > prediction && total < 0-under_threshold) {
            td.classList.add("betunder");
        }

        span.appendChild(tbl);
        total_div.appendChild(span);
    }
    return row.appendChild(td);
}

function createValues(row, gamePk, bet, value, prediction, total, over_under, over_threshold, under_threshold, park_factor) {
    let td = document.createElement("td");
    td.setAttribute('id', `${gamePk}_${value}`);

    let adjusted_park_factor = Math.round(park_factor * 2) / 2;
    let high_park_factor = park_factor + 0.5;
    let low_park_factor = park_factor - 0.5;
    let is_high = over_under >= high_park_factor && prediction >= high_park_factor;
    let is_low = over_under <= low_park_factor && prediction <= low_park_factor;
    let is_neutral = (over_under > low_park_factor && over_under < high_park_factor) && (prediction > low_park_factor && prediction < high_park_factor);
    if (bet !== "TBD" && bet !== "No Value") {
        td.innerHTML = `${bet}`;
        if (is_high || is_low) {
            td.classList.add("betbad");
        } else if (is_neutral) {
            td.classList.add("betneutral");
        } else {
            td.classList.add("betgood");
        }
    } else {
        td.innerHTML = bet;
    }
    return row.appendChild(td);
}

function populateTables(game) {
    let row = document.createElement("tr");
    let game_time = new Date(game.gameData.game_time).toLocaleString('en-US', {hour: 'numeric', minute: 'numeric', hour12: true});
    let prediction = game.valueData.prediction;
    let pred_name = [
        'Park', 
        'Wind', 
        'Temp', 
        'Ump', 
        `${game.gameData.away_team_short} Defense`, 
        `${game.gameData.home_team_short} Defense`, 
        `${game.gameData.away_team_short} vs. ${game.gameData.home_pitcher.fullName}`, 
        `${game.gameData.home_team_short} vs. ${game.gameData.away_pitcher.fullName}`,
        'Handicap'
    ];
    let total = game.valueData.total;
    let over_under = game.betData.over_under;
    let over_120 = game.valueData.over_120, over_100 = game.valueData.over_100;
    let under_120 = game.valueData.under_120, under_100 = game.valueData.under_100;
    let thresholds = [
        ['', '<strong>Over</strong>', '<strong>Under</strong>'],
        ['<strong>120%</strong>', over_120, under_120], 
        ['<strong>100%</strong>', over_100, under_100]
    ];
    let weather = game.gameData.weather;
    if (weather !== "TBD") {
        if (weather.condition === "Drizzle" || weather.condition === "Rain" || weather.condition === "Snow") {
            row.style.border = "3px solid #dc3545";
        }
        if (game.gameData.home_team_full === "Chicago Cubs" && data.direction === "In" && data.speed >= 10) {
            row.style.border = "3px solid #dc3545";
        }
    }
    if (prediction === "TBD") {
        row.classList.add('grayout');
    }
    createTeams(
        row, 
        game.gameData.away_team_short, 
        logos[game.gameData.away_team_full], 
        game.gameData.home_team_short, 
        logos[game.gameData.home_team_full]
    );
    createGameTime(row, game_time);
    createPrediction(
        row, 
        prediction, 
        game.predData, 
        pred_name, 
        game.gameData.home_team_full,
        game.gameData.ump
    );
    createLines(
        row, 
        game.betData.idfoevent, 
        over_under, 
        game.betData.over_line, 
        game.betData.under_line
    );
    createTotal(
        row, 
        total,
        game.betData.idfoselection,
        thresholds,
        prediction, 
        over_under, 
        over_100, 
        under_100
    );
    createValues(
        row, 
        game.gameData.gamePk,
        game.valueData.value_120, 
        "120", 
        prediction, 
        total, 
        over_under, 
        over_120, 
        under_120,
        game.predData.park_factor
    );
    createValues(
        row, 
        game.gameData.gamePk,
        game.valueData.value_100, 
        "100", 
        prediction, 
        total, 
        over_under, 
        over_100, 
        under_100,
        game.predData.park_factor
    );
    return table.appendChild(row);
}

function changeClass(el, _class) {
    el.classList.add(_class);
    setTimeout(() => {
        el.classList.remove(_class);
    }, 5500);
}

function updateLine(el_id, odds_type, o, u) {
    var el = document.querySelector(`#${CSS.escape(el_id)}`);
    var over_el = el.nextSibling.childNodes[0];
    var under_el = el.nextSibling.childNodes[1];
    var over = parseInt(over_el.innerHTML.split(' ')[0]);
    var under = parseInt(under_el.innerHTML.split(' ')[0]);
    if (over !== o || under !== u) {
        over_el.innerHTML = `${o} O`;
        under_el.innerHTML = `${u} U`;
        if (o > over) {
            changeClass(over_el, 'price-up');
        }
        if (o < over) {
            changeClass(over_el, 'price-down');
        }
        if (u > under) {
            changeClass(under_el, 'price-up');
        }
        if (u < under) {
            changeClass(under_el, 'price-down');
        }
    }
    if (el.innerHTML !== odds_type) {
        el.innerHTML = odds_type;
        if (el.innerHTML > odds_type) {
            changeClass(el.parentElement.parentElement, 'price-down');
        }
        if (el.innerHTML < odds_type) {
            changeClass(el.parentElement.parentElement, 'price-up');
        }
    }
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

function changeValue(el_id, value, total, over_threshold, under_threshold) {
    var el = document.querySelector(`#${CSS.escape(el_id)}`);
    if (el.innerHTML > value) {
        el.innerHTML = value;
        changeClass(el, 'bet-down');
        if (total <= over_threshold) {
            el.setAttribute('class', '');
        }
    } else if (el.innerHTML < value) {
        el.innerHTML = value;
        changeClass(el, 'bet-up');
        if (total >= 0-under_threshold) {
            el.setAttribute('class', '');
        }
    } else if (el.innerHTML === 'No Value' && total > over_threshold) {
        el.innerHTML = value;
        el.classList.add("betover");
    } else if (el.innerHTML === 'No Value' && total < 0-under_threshold) {
        el.innerHTML = value;
        el.classList.add("betunder");
    } else if (el.innerHTML != 'No Value' && total <= 0.50 && total >= -0.50) {
        el.innerHTML = 'No Value';
        el.setAttribute('class', '');
    }
}

function noGames() {
    var table = document.querySelector("#slate");
    var row = document.createElement("tr");
    var td = document.createElement("td");
    td.innerHTML = "No games";
    td.colSpan = document.getElementsByTagName('th').length;
    td.style.textAlign = "center";
    row.appendChild(td);
    table.appendChild(row);
    no_games = true;
}

function changeLine(game, over_under, prediction, over_threshold, under_threshold, over_120, under_120, over, under, ids) {
    socket.emit('changeLine', {'game': game, 'over_under': over_under, 'prediction': prediction, 'over_threshold': over_threshold, 'under_threshold': under_threshold, 'over_120': over_120, 'under_120': under_120, 'over': over, 'under': under, 'ids': ids});
}

// function updateOdds() {
//     getFanduel().then(fd => {
//         fd.events.forEach(e => {
//             // console.log(e);
//             if (data.find(x => x.game.market.idfoevent === e.idfoevent)) {
//                 var game = data.find(x => x.game.market.idfoevent === e.idfoevent);
//                 var market = e.markets.find(x => x.idfomarkettype === 48555.1);
//                 var over = getMoneyLine(market.selections.find(x => x.name === "Over"));
//                 var under = getMoneyLine(market.selections.find(x => x.name === "Under"));
//                 var ids = {"actual_id": market.idfoevent, "total_id": market.selections.find(x => x.name === "Over").idfoselection, "value_id_100": `${game.gamePk}_100`, "value_id_120": `${game.gamePk}_120`};
//                 var now = new Date();
//                 var game_time = new Date(market.tsstart);
//                 if (now.getTime() >= game_time.getTime()) {
//                     $(document.querySelector(`#${CSS.escape(game.gamePk)}`)).closest('tr').remove();
//                     callApi(main_url, find_date).then(data => {
//                         active_games = data.games.filter(x => x.status.codedGameState === "P" || x.status.codedGameState === "S" ).length;
//                         if (active_games === 0) {
//                             noGames();
//                         }
//                     });
//                 }
//                 changeLine(game.game, market.currentmatchhandicap, game.prediction, game.over_threshold, game.under_threshold, game.over_120, game.under_120, over, under, ids);
//             }
//         });
//     });
// }

socket.on("lineChange", data => {
    try {
        updateLine(data.ids.actual_id, data.over_under, data.over, data.under);
        changePrice(data.ids.total_id, data.new_total);
        changeValue(data.ids.value_id_100, data.bet, data.new_total, data.over_threshold, data.under_threshold);
        changeValue(data.ids.value_id_120, data.bet, data.new_total, data.over_120, data.under_120);
    }
    catch (error) {
        console.log(error);
    }
});

// main loop //

document.addEventListener('DOMContentLoaded', () => {
    if (data.length !== 0) {
        data.forEach(game => {
            if (game.betData.live_bet) {
                populateTables(game);
            }
        });
    } else {
        noGames();
    }
});

// (function mainLoop() {
//     let rand = Math.floor(Math.random() * 10) + 10;
//     if (!no_games) {
//         setTimeout(() => {
//             updateOdds();
//             mainLoop();
//         }, rand * 1000);
//     }
// }());
