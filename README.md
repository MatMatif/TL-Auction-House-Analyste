# TL-Auction-House-Analyste
## Pourquoi JavaScript n'a pas besoin de visibilité ?
### Manipulation directe du DOM :

<p>Avec JavaScript, vous interagissez directement avec les éléments du DOM, sans tenir compte de leur visibilité ou de leur position à l'écran</p>
<p>Exemple : Un bouton masqué via CSS (display: none ou visibility: hidden) peut toujours être cliqué avec JavaScript.</p>

### Pas de vérification de l'état par le navigateur :

<p>Selenium impose des contraintes comme vérifier que l'élément est visible ou cliquable. En JavaScript, ces vérifications sont ignorées, ce qui permet de simuler un clic même si l'élément est hors champ.</p>
