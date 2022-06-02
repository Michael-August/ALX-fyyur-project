window.parseISOString = function parseISOString(s) {
	var b = s.split(/\D+/);
	return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

let trash_venue = document.querySelectorAll('.del_venue')
// let trash_artist = document.querySelectorAll('.del_artist')

trash_venue.forEach((venue, index) => {
	trash_venue[index].addEventListener('click', (e) => {
		let venue_id = e.target.dataset.id
		fetch('/venues/' + venue_id, {
			method: 'DELETE'
		})
		.then((response) => {
			e.target.parentElement.remove()
			window.location.replace("/")
			return response.json()
		})
		.then((jsonResponse) => {
			
		})
	})
});

// trash_artist.forEach((artist, index) => {
// 	trash_artist[index].addEventListener('click', (e) => {
// 		console.log(e.target.parentElement, e);
// 	})
// });
