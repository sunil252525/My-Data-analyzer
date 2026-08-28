<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Number Splitter App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            margin: 0;
            padding: 15px;
        }
        h2 {
            text-align: center;
            color: #333;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 100px 10px;
            font-size: 14px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
            resize: vertical;
        }
        button {
            width: 100%;
            padding: 12px;
            background-color: #28a745;
            color: white;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            margin-top: 10px;
            cursor: pointer;
        }
        button:hover {
            background-color: #218838;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .card {
            background: #fafafa;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 10px;
        }
        .card h3 {
            margin-top: 0;
            font-size: 16px;
            color: #007bff;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
        }
        .main-group {
            font-weight: bold;
            background: #e9ecef;
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 10px;
            font-size: 13px;
            word-break: break-all;
        }
        .sub-group {
            background: #fff;
            border: 1px solid #eee;
            padding: 6px;
            margin-bottom: 6px;
            border-radius: 4px;
            font-size: 13px;
            word-break: break-all;
        }
    </style>
</head>
<body>

<div class="container">
    <h2>नंबर स्प्रेडर व ग्रुप जनरेटर</h2>
    <label><b>यहाँ अपने 90 नंबर कॉमा (,) लगाकर पेस्ट करें:</b></label>
    <textarea id="inputData" placeholder="00, 01, 02, 03..."></textarea>
    <button onclick="processNumbers()">जनरेट करें (Generate)</button>

    <div class="grid" id="output"></div>
</div>

<script>
function shuffle(array) {
    let currentIndex = array.length, randomIndex;
    while (currentIndex != 0) {
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;
        [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
    }
    return array;
}

function processNumbers() {
    let rawInput = document.getElementById("inputData").value;
    if (!rawInput.trim()) {
        alert("कृपया नंबर दर्ज करें!");
        return;
    }

    // नंबरों को अलग करें
    let numbers = rawInput.split(',').map(num => num.trim()).filter(num => num !== "");

    // नंबरों को रैंडम मिक्स करें
    numbers = shuffle(numbers);

    // 4 ग्रुप में बांटें
    let groupA = numbers.slice(0, 20);
    let groupB = numbers.slice(20, 40);
    let groupC = numbers.slice(40, 65);
    let groupD = numbers.slice(65, 90);

    let groups = [
        { name: "ग्रुप A (20 नंबर)", data: groupA },
        { name: "ग्रुप B (20 नंबर)", data: groupB },
        { name: "ग्रुप C (25 नंबर)", data: groupC },
        { name: "ग्रुप D (25 नंबर)", data: groupD }
    ];

    let outputHtml = "";

    groups.forEach(grp => {
        if (grp.data.length === 0) return;

        let mainStr = grp.data.join(", ");
        
        // सब-ग्रुप्स बनाना (विभिन्न सिंबल के साथ)
        let sub1 = grp.data.slice(0, 5).join(" / ") + " (100)";
        let sub2 = grp.data.slice(5, 9).join(" _ ") + " (100)";
        let sub3 = grp.data.slice(9, 13).join(" - ") + " (100)";
        let sub4 = grp.data.slice(13, 16).join(", ") + " (100)";
        let sub5 = grp.data.slice(16).join(" . ") + " (100)";

        outputHtml += `
            <div class="card">
                <h3>${grp.name}</h3>
                <div class="main-group">${mainStr}</div>
                <div class="sub-group">${sub1}</div>
                <div class="sub-group">${sub2}</div>
                <div class="sub-group">${sub3}</div>
                <div class="sub-group">${sub4}</div>
                <div class="sub-group">${sub5}</div>
            </div>
        `;
    });

    document.getElementById("output").innerHTML = outputHtml;
}
</script>

</body>
</html>
