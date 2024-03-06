import { tsParticles } from 'https://cdn.jsdelivr.net/npm/@tsparticles/engine@3.3.0/+esm';
import { loadPolygonMaskPlugin } from 'https://cdn.jsdelivr.net/npm/@tsparticles/plugin-polygon-mask@3.3.0/+esm';
import { loadFull } from 'https://cdn.jsdelivr.net/npm/tsparticles@3.3.0/+esm';

const config = await (await fetch("static/particles.json")).json();

const field = document.getElementById('field');
    
field.addEventListener('keypress', showResult);

(async () => {
    await loadFull(tsParticles);
    await loadPolygonMaskPlugin(tsParticles);

    await tsParticles
    .load({
      id: "tsparticles",
      options: config,
    });
})();


async function generateSvg(uid) {
    let svg_link = `https://danmarshall.github.io/google-font-to-svg-path/?font-select=Gurajada&font-variant=regular&input-union=false&input-filled=true&input-kerning=true&input-separate=false&input-text=${uid}&input-bezier-accuracy=&dxf-units=cm&input-size=100&input-fill=%23000&input-stroke=%23000&input-strokeWidth=0.25mm&input-fill-rule=evenodd`
    return fetch(svg_link)
    .then(response => response.text())
    .then(data => {
        let svg = new Blob([data], {type: 'image/svg+xml'});
        let url = URL.createObjectURL(svg);
        return url;
    });
}

async function showResult(ev) {
    const field = document.getElementById('field');
    
    if (ev.key === "Enter") {
        let input = field.value;
        let endpoint = `/encode?url=${input}`;

        try {
            const response = await fetch(endpoint, {
                method: 'GET',
            });
            const data = await response.json();
            let url_id = data.url.split('/')[1];
            let svg_url = await generateSvg(url_id); 
            // We now change the particle config svg to the new svg
            config.polygon.url = `https://danmarshall.github.io/google-font-to-svg-path/?font-select=Gurajada&font-variant=regular&input-union=false&input-filled=true&input-kerning=true&input-separate=false&input-text=${url_id}&input-bezier-accuracy=&dxf-units=cm&input-size=100&input-fill=%23000&input-stroke=%23000&input-strokeWidth=0.25mm&input-fill-rule=evenodd`
            // We create a new div that will contain the particles
            let div = document.createElement('div');
            div.id = 'tsparticles_result';
            (async () => {
                await tsParticles
                .load({
                  id: "tsparticles",
                  options: config,
                });
            })();
        } catch (error) {
            console.error('Error:', error);
        }
    }
};


// snipResult.addEventListener('click', function() {
//     window.location.href = `http://localhost:8000/${result}`});

// snipResult.innerHTML = result;