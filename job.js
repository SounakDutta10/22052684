const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const TEST_SERVER_URL = "http://20.244.56.144/evaluation-service/numbers/";
const WINDOW_SIZE = 10;
let storedNumbers = [];

function isValidNumberId(id) {
    return ['p', 'f', 'e', 'r'].includes(id);
}

app.get('/numbers/:numberid', async (req, res) => {
    const startTime = Date.now();
    const numberId = req.params.numberid;

    if (!isValidNumberId(numberId)) {
        return res.status(400).json({ error: "Invalid number ID. Use 'p', 'f', 'e', or 'r'." });
    }

    try {
        const response = await axios.get(`${TEST_SERVER_URL}${numberId}`, { timeout: 500 });
        const numbers = response.data.numbers || [];
        const prevState = [...storedNumbers];

        numbers.forEach(num => {
            if (!storedNumbers.includes(num)) {
                storedNumbers.push(num);
            }
        });

        if (storedNumbers.length > WINDOW_SIZE) {
            storedNumbers = storedNumbers.slice(-WINDOW_SIZE);
        }

        const avg = storedNumbers.length > 0 
            ? (storedNumbers.reduce((a, b) => a + b, 0) / storedNumbers.length).toFixed(2) 
            : 0;

        const responseTimeMs = Date.now() - startTime;
        if (responseTimeMs > 500) {
            return res.status(500).json({ error: "Response time exceeded 500ms" });
        }

        res.status(200).json({
            windowPrevState: prevState,
            windowCurrState: storedNumbers,
            numbers,
            avg
        });
    } catch (error) {
        res.status(500).json({ error: "Failed to fetch numbers within 500ms" });
    }
});

const PORT = 9876;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
