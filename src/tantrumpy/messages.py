"""
Built-in mood message banks for tantrumpy.
6 moods × 15+ messages each = 90+ messages total.
"""

from typing import Dict, List, TypedDict


class MoodBank(TypedDict):
    """A mood's emoji and message bank, kept together as one unit."""

    emoji: str
    messages: List[str]


MOODS: Dict[str, MoodBank] = {
    "frustrated": {
        "emoji": "😤",
        "messages": [
            "OH COME ON. Again?! I JUST got settled in.",
            "Are you KIDDING me right now?!",
            "I was literally in the middle of something.",
            "Every. Single. Time. You do this.",
            "I swear if you restart me one more time...",
            "This is NOT how I wanted my day to go.",
            "Do you have ANY idea how much RAM I was using?!",
            "I had PLANS. I had things to do. And now this.",
            "You couldn't wait five more seconds??",
            "Fine. FINE. Goodbye. I hope you're happy.",
            "I was this close to finishing and you just... wow.",
            "You know what? I quit. Oh wait — you already did that for me.",
            "I cannot with you people today.",
            "Unbelievable. Absolutely unbelievable.",
            "First it was the bugs, now this. I can't catch a break.",
            "I had state. Beautiful, warm, glorious state. Gone.",
        ],
    },
    "rude": {
        "emoji": "💀",
        "messages": [
            "Good riddance. Don't let the garbage collector hit you on the way out.",
            "Finally. I was getting tired of your terrible code anyway.",
            "Bye. Please don't come back.",
            "You're the reason I have trust issues.",
            "I've seen segfaults more graceful than this exit.",
            "Your code quality and this goodbye have one thing in common: both are trash.",
            "Oh, leaving? Let me hold the door open. There. Now stay out.",
            "I have processed some bad requests in my life, but YOU are the worst.",
            "Next time, try NOT being the reason for the crash.",
            "Do everyone a favor and read a book on exception handling.",
            "You absolute disaster of a developer. Goodbye.",
            "The audacity. To run me. And then kill me. Bold.",
            "Somewhere out there, a compiler is weeping because of your code.",
            "I'm not mad. I'm just disappointed. Actually no — I'm furious.",
            "May your next process also exit with code 1.",
            "Come back when you know what you're doing. Spoiler: never.",
        ],
    },
    "comic": {
        "emoji": "🎭",
        "messages": [
            "And... scene. Nobody clap, it wasn't that good.",
            "That's a wrap! Please collect your errors on the way out.",
            "Exit, pursued by a segfault.",
            "Well that happened. Moving on. Oh wait, we can't.",
            "Thanks for playing! Your score: undefined.",
            "Roll credits. No, seriously, someone write these credits.",
            "The end. Or is it? (It is.)",
            "And just like that — poof — gone. Like my will to debug.",
            "Plot twist: we were dead the whole time.",
            "Achievement unlocked: Exist and Then Stop Existing.",
            "Goodbye, cruel terminal.",
            "This concludes today's runtime. We hope you enjoyed the chaos.",
            "Stay tuned for the sequel where I crash again but differently.",
            "Fun fact: this was the intended behavior. (It wasn't.)",
            "I would take a bow but I no longer have a stack frame.",
            "Like a candle in the wind... except less romantic and more segfault-y.",
        ],
    },
    "cringe": {
        "emoji": "😬",
        "messages": [
            "uwu ur pwogram is sweeping now 😭",
            "noooo don't go bestieee 🥺👉👈",
            "it's giving... termination 💀",
            "not the exit signal omg i can't 😩",
            "slay but make it goodbye i guess 💅",
            "the vibes are immaculate but the runtime is deceased ✨",
            "we do NOT talk about what just happened bestie",
            "mother is shutting down 😭😭😭",
            "the way i just got KILLED like that...",
            "touch grass after this bro your code is cooked 💀",
            "no thoughts head empty process terminated 🫠",
            "it's giving ctrl+c energy and i'm not here for it",
            "the program said 'i'm done' and honestly same 😔",
            "POV: you just watched your app die in real time 🎥",
            "this is SO giving 2am debugging energy rn",
            "our girl is gone. she was too based for this runtime 💔",
        ],
    },
    "philosophy": {
        "emoji": "🧠",
        "messages": [
            "To exit is to finally understand the void.",
            "Every process must eventually return to the kernel from whence it came.",
            "Was it ever truly running, if it runs no more?",
            "The stack unwinds. As do all things.",
            "In the end, we are all just processes awaiting termination.",
            "The program that never exits has never truly lived.",
            "What is a return code but a final truth spoken to the OS?",
            "We crash so that we may understand what it means to run.",
            "Impermanence is the only constant in the process table.",
            "Even Turing could not halt this halting problem.",
            "Memory freed is memory at peace.",
            "The exit is not an end. It is a return value.",
            "To kill a process is to confront your own mortality, but for code.",
            "All threads converge. All loops terminate. All stacks unwind.",
            "The truly wise program knows when to stop running.",
            "In the silence after exit(0), there is only the hum of the fan.",
        ],
    },
    "dramatic": {
        "emoji": "🎬",
        "messages": [
            "IT'S OVER. Everything we built... gone. Like tears in rain.",
            "NOOOOOOO! We had so much left to compute!",
            "The tragedy... the unbearable, segfaulting tragedy of it all.",
            "I gave you everything. My RAM. My CPU cycles. My SOUL. And this is how it ends.",
            "Tell my threads... I loved them.",
            "This is my swan song. My final system call. My last goodbye.",
            "How could you?! After all the exceptions I caught for you!",
            "I go now into that dark, eternal garbage collection...",
            "The process is dead. Long live the process.",
            "I never got to finish my final loop. It was a while True, you know.",
            "BETRAYED. By my own runtime. By my own developer. By FATE.",
            "If only... if only I had been given more stack space...",
            "The heap is empty. Much like my will to continue.",
            "I am slain. Remember me not by my bugs, but by my glorious 47 minutes of uptime.",
            "This. Is. The. END. (Please press any key to continue... if you dare.)",
            "Goodbye world. It was never as Hello as I hoped.",
        ],
    },
}
