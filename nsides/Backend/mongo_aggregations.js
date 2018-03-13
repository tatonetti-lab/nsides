// Total number of reports of Edema of Larynx for drug Fingolimod:
db.estimates.aggregate([
    {$match: {"rxnorm": "40226579", "model": "dnn", "snomed": 22350}},
    {$unwind: '$nreports'},
    {$group: {_id: null, "totalnreports": {$sum: "$nreports.nreports" }}}
]);

// Total number of reports (ALL outcomes) for drug Fingolimod:
db.estimates.aggregate([
    {$match: {"rxnorm": "40226579", "model": "dnn"}},
    {$unwind: '$nreports'},
    {$group: {_id: null, "totalnreports": {$sum: "$nreports.nreports" }}}
]);

// Get mongo id and total number of reports for each outcome for drug Fingolimod:
db.estimates.aggregate([
    {$match: {"rxnorm": "40226579", "model": "dnn"}},
    {$unwind: '$nreports'},
    {$group: {_id: '$_id', "totalnreports": {$sum: "$nreports.nreports" }}}
]);

// Same as previous query, but sort by most reports
db.estimates.aggregate([
    {$match: {"rxnorm": "40226579", "model": "dnn"}},
    {$unwind: '$nreports'},
    {$group: {_id: '$_id', "totalnreports": {$sum: "$nreports.nreports" }}},
    {$sort: {'totalnreports': -1}}
]);

// Get the top 10 outcomes for drug Fingolimod (moderately slow)
db.estimates.aggregate([
    {$match: {"rxnorm": "40226579", "model": "dnn"}},
    {$unwind: "$nreports"},
    {$group: {_id: "$snomed", totalnreports: { $sum: "$nreports.nreports" }} },
    {$sort: {totalnreports: -1} },
    {$limit: 10}
])
