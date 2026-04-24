// Graphics n stuff
const icon_width = 79,
      icon_height = 79,
      num_icons = 9,
      time_per_icon = 100,
      indexes = [0,0,0],
      iconMap = ["banana", "seven", "cherry", "plum", "orange", "bell", "bar", "lemon", "melon"];

const roll = (reel, offset = 0, target = null) => {
    let delta = (offset + 2) * num_icons + Math.round(Math.random() * num_icons);
    const style = getComputedStyle(reel),
          backgroundPositionY = parseFloat(style["background-position-y"]);
          
    if (target) {
		// calculate delta to target
		const currentIndex = backgroundPositionY / icon_height;
		delta = target - currentIndex + (offset + 2) * num_icons;
	}
    
    return new Promise((resolve, reject) => {
        
        const
            targetBackgroundPositionY = backgroundPositionY + delta * icon_height,
            normTargetBackgroundPositionY = targetBackgroundPositionY%(num_icons*icon_height);
        
        setTimeout(() => { 
			reel.style.transition = `background-position-y ${(8 + 1 * delta) * time_per_icon}ms cubic-bezier(.41,-0.01,.63,1.09)`;
			reel.style.backgroundPositionY = `${backgroundPositionY + delta * icon_height}px`;
		}, offset * 150);
			
		// After animation
		setTimeout(() => {
			// Reset position, so that it doesn't get higher without limit
			reel.style.transition = `none`;
			reel.style.backgroundPositionY = `${normTargetBackgroundPositionY}px`;
			// Resolve this promise
			resolve(delta%num_icons);
		}, (8 + 1 * delta) * time_per_icon + offset * 150);
    });
};

function rollAll(targets = null) {
    const reelsList = document.querySelectorAll('.slots > .reel');

    // const targets = window.timesRolled && window.timesRolled%2 ? [6, 6, 6] : null;
	// if (!window.timesRolled) window.timesRolled = 0;
	// window.timesRolled++;
    
    Promise
        // Activate each reel, must convert NodeList to Array for this with spread operator
		.all( [...reelsList].map((reel, i) => roll(reel, i, targets ? targets[i] : null)) )	
		
		// When all reels done animating (all promises solve)
		.then((deltas) => {
			// add up indexes
			deltas.forEach((delta, i) => indexes[i] = (indexes[i] + delta)%num_icons);

        // Win conditions
        if (indexes[0] == indexes[1] || indexes[1] == indexes[2]) {
            const winCls = indexes[0] == indexes[2] ? "win2" : "win1";
            document.querySelector(".slots").classList.add(winCls);
            setTimeout(() => document.querySelector(".slots").classList.remove(winCls), 2000)
        }
        })
    
    console.log("reels found:", reelsList.length)   // should print 3
    console.log("targets:", targets)
}

// Server stuff
const evtSource = new EventSource("http://localhost:8000/stream")

evtSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log("Received:", data)

  if (data.type === "scene") {
    // hide all scenes, show the target one
    document.querySelectorAll(".scene").forEach(el => el.classList.remove("active"))
    document.getElementById("scene-" + data.name).classList.add("active")
  }

  if (data.type === "roll") {
    rollAll(data.targets)
  }

  if (data.type === "balance") {
    document.getElementById("balance-display").textContent = data.balance
  }
}

document.addEventListener("keydown", (e) => {
    const key = e.key === " " ? "space" : e.key
    console.log("Key pressed:", key)
    fetch("http://localhost:8000/keypress", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({key: key})
    }).then(() => console.log("Keypress sent to Python"))
})

evtSource.onerror = () => {
  console.error("SSE connection lost")
}
