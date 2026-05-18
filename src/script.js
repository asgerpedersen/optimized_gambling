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
    const reelsList = document.querySelectorAll('.slots > .reel')
    let settledCount = 0

    Promise
        .all([...reelsList].map((reel, i) => 
            roll(reel, i, targets !== null ? targets[i] : null).then((delta) => {
                settledCount++
                if (settledCount === 2) {
                    fetch("http://localhost:8000/partial-stop", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({status: "partial"})
                    })
                }
                return delta
            })
        ))
        .then((deltas) => {
            deltas.forEach((delta, i) => indexes[i] = (indexes[i] + delta) % num_icons)

            fetch("http://localhost:8000/animation-done", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({status: "done"})
            })
            console.log("animation finished")

            if (indexes[0] == indexes[1] && indexes[1] == indexes[2]) {
                document.querySelector(".slots").classList.add("win2")
                setTimeout(() => document.querySelector(".slots").classList.remove("win2"), 2000)
            }
        })

    console.log("reels found:", reelsList.length)
    console.log("targets:", targets)
}

// Server stuff
const evtSource = new EventSource("http://localhost:8000/stream")

evtSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log("Received:", data)

  if (data.type === "scene") {
    document.querySelectorAll(".scene").forEach(el => el.classList.remove("active"))
    const target = document.getElementById(data.name)
    console.log("switching to scene:", data.name, "element found:", target)
    target.classList.add("active")
}

  if (data.type === "block-start") {
    document.getElementById("block-number-auto").textContent = data.block_number
    document.getElementById("block-number-manual").textContent = data.block_number
    document.getElementById("block-number-global").textContent = data.block_number
    }

  if (data.name === "pleasure-rating") {
    document.querySelectorAll(".rating-btn").forEach(btn => btn.classList.remove("selected"))
    }

  if (data.type === "roll") {
    rollAll(data.targets)
  }

  if (data.type === "balance") {
    document.getElementById("balance-display-extra").textContent = data.balance
    document.getElementById("balance-display-slots").textContent = data.balance
}

  if (data.type === "global_balance") {
        document.getElementById("payout-balance").textContent = data.global_balance
        document.getElementById("payout-balance-exit").textContent = data.global_balance
  }

  if (data.type == "spins-left") {
    document.getElementById("current-spins-left").textContent = data.spins_left
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

    // handle pleasure rating keys
    const pleasureScene = document.getElementById("pleasure-rating")
    if (pleasureScene.classList.contains("active")) {
        const rating = parseInt(e.key)
        if (rating >= 1 && rating <= 6) {
            // highlight the corresponding button
            document.querySelectorAll(".rating-btn").forEach(btn => btn.classList.remove("selected"))
            document.querySelector(`.rating-btn[data-value="${rating}"]`).classList.add("selected")

            // send rating to Python
            fetch("http://localhost:8000/rating", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({rating: rating})
            })
        }
    }
})

// Click listner
document.querySelectorAll(".rating-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        // highlight selected button
        document.querySelectorAll(".rating-btn").forEach(b => b.classList.remove("selected"))
        btn.classList.add("selected")

        // send rating to Python
        const rating = parseInt(btn.dataset.value)
        fetch("http://localhost:8000/rating", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({rating: rating})
        })
    })
})


evtSource.onerror = () => {
  console.error("SSE connection lost")
}


// Enter fullscreen when the page loads
document.addEventListener("DOMContentLoaded", () => {
    document.documentElement.requestFullscreen()
})

document.getElementById("start-btn").addEventListener("click", () => {
    document.documentElement.requestFullscreen()
    document.body.style.cursor = "none"
    fetch("http://localhost:8000/keypress", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({key: "start"})
    })
})