function toggleActive(selection){
    selection.classed('active', !selection.classed('active'));
}

window.addEventListener('load', function(){
    let punchcard = d3.select('.punchcard');
    let container = d3.select(punchcard.node().parentNode);
    let nav = container.select('aside');

    nav.selectAll('header a')
      .on('click', function(){
        const id =  new URL(this.href).hash
        nav.select('.card.active').classed('active', false);
        nav.select(id).classed('active', true);
        d3.event.preventDefault();
      })
    nav.selectAll('tr')
       .style('cursor', 'pointer')
       .on('click', function(){
         d3.select(this).call(toggleActive);
         const actives = nav.node().querySelectorAll('tr.active');
         const bars = nav.node().querySelectorAll('tr.active .bar');

         const columns = container.selectAll('.column').data(actives);

         const headers = container.selectAll('.column header').data(actives);
         headers.text(d => d.dataset.name);
         headers.exit().text('');

         const items = container.selectAll('.column ul.axis').data(bars);
         const gnds = items.selectAll('.gnd')
           .data(d => d.querySelectorAll('.value'), function(d){return d ? d.dataset.name : this.dataset.gnd})
           gnds.style('height', d => d.dataset.percent + '%')
             .style('width', d => d.dataset.percent + '%')
           gnds.exit()
               .style('height', 0)
               .style('width', 0)
       })
})
