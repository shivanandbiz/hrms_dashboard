// Daily Quotes Database
const dailyQuotes = [
    {
        text: "Life is 10% what happens to us and 90% how we react to it.",
        author: "Dennis P. Kimbro"
    },
    {
        text: "The only way to do great work is to love what you do.",
        author: "Steve Jobs"
    },
    {
        text: "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        author: "Winston Churchill"
    },
    {
        text: "Believe you can and you're halfway there.",
        author: "Theodore Roosevelt"
    },
    {
        text: "The future belongs to those who believe in the beauty of their dreams.",
        author: "Eleanor Roosevelt"
    },
    {
        text: "It does not matter how slowly you go as long as you do not stop.",
        author: "Confucius"
    },
    {
        text: "Everything you've ever wanted is on the other side of fear.",
        author: "George Addair"
    },
    {
        text: "Success is not how high you have climbed, but how you make a positive difference to the world.",
        author: "Roy T. Bennett"
    },
    {
        text: "Don't watch the clock; do what it does. Keep going.",
        author: "Sam Levenson"
    },
    {
        text: "The only impossible journey is the one you never begin.",
        author: "Tony Robbins"
    }
];

// Set daily quote based on date
function setDailyQuote() {
    const today = new Date();
    const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
    const quoteIndex = dayOfYear % dailyQuotes.length;
    const quote = dailyQuotes[quoteIndex];

    const quoteText = document.getElementById('quote-text');
    const quoteAuthor = document.getElementById('quote-author');

    if (quoteText && quoteAuthor) {
        quoteText.textContent = quote.text;
        quoteAuthor.textContent = `- ${quote.author}`;
    }
}

// Set greeting based on time of day
function setGreeting() {
    const hour = new Date().getHours();
    let greeting = "Good Morning";

    if (hour >= 12 && hour < 17) {
        greeting = "Good Afternoon";
    } else if (hour >= 17) {
        greeting = "Good Evening";
    }

    const greetingElement = document.getElementById('greeting-text');
    if (greetingElement) {
        greetingElement.textContent = greeting;
    }
}

// Initialize quote and greeting
document.addEventListener('DOMContentLoaded', function () {
    setGreeting();
    setDailyQuote();
});
