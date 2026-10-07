const scenarios = [['Normal','Town02','S1_Town02_Normal'],['No warnings','Town10','S2_Town10_NoWarnings'],['Rainy','Town04','S3_Town04_Rainy'],['Curve','Town05','S4_Town05_Curve'],['Nighttime','Town02_2','S5_Town02_2_Nighttime'],['Trucks','Town10HD_2','S6_Town10HD_2_Trucks']];
const tabs = [...document.querySelectorAll('[role="tab"]')];
function selectScenario(index, focus = false) {
  const [name, map, directory] = scenarios[index];
  tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(i === index)); tab.tabIndex = i === index ? 0 : -1; });
  document.getElementById('scenario-name').textContent = name;
  document.getElementById('scenario-map').textContent = map;
  document.getElementById('scenario-directory').textContent = directory;
  document.getElementById('scenario-link').href = `https://github.com/shuo9898-zs/DualSense/tree/main/scenarios/${directory}`;
  document.getElementById('scenario-panel').setAttribute('aria-labelledby', tabs[index].id);
  if (focus) tabs[index].focus();
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectScenario(index));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    else if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) { event.preventDefault(); selectScenario(next, true); }
  });
});
