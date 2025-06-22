const div = document.querySelector(".github-topic-projects");

async function getDataBatch(page) {
  const response = await fetch(
    `https://api.github.com/search/repositories?q=topic:pan-os-upgrade&per_page=100&page=${page}`,
    { headers: { Accept: "application/vnd.github.mercy-preview+json" } },
  );
  const data = await response.json();
  return data;
}

async function getData() {
  let page = 1;
  let data = [];
  let dataBatch = await getDataBatch(page);
  data = data.concat(dataBatch.items);
  const totalCount = dataBatch.total_count;
  while (data.length < totalCount) {
    page += 1;
    dataBatch = await getDataBatch(page);
    data = data.concat(dataBatch.items);
  }
  return data;
}


function shuffle(array) {
  var currentIndex = array.length,
    temporaryValue,
    randomIndex;
  while (0 !== currentIndex) {
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }
  return array;
}

async function showRandomAnnouncement(groupId, timeInterval) {
  const announcePanOsUpgrade = document.getElementById(groupId);
  if (announcePanOsUpgrade) {
    let children = [].slice.call(announcePanOsUpgrade.children);
    children = shuffle(children);
    let index = 0;
    const announceRandom = () => {
      children.forEach((el, i) => {
        el.style.display = "none";
      });
      children[index].style.display = "block";
      index = (index + 1) % children.length;
    };
    announceRandom();
    setInterval(announceRandom, timeInterval);
  }
}

async function main() {
  if (div) {
    data = await getData();
    div.innerHTML = "<ul></ul>";
    const ul = document.querySelector(".github-topic-projects ul");
    data.forEach((v) => {
      if (v.full_name === "cdot65/pan-os-upgrade") {
        return;
      }
      const li = document.createElement("li");
      li.innerHTML = `<a href="${v.html_url}" target="_blank">★ ${v.stargazers_count} - ${v.full_name}</a> by <a href="${v.owner.html_url}" target="_blank">@${v.owner.login}</a>`;
      ul.append(li);
    });
  }

  showRandomAnnouncement("announce-left", 5000);
  showRandomAnnouncement("announce-right", 10000);
}

main();
