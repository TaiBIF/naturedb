import { fetchData } from './utils.js';
import { default as $n } from './setnil.js';
import Formant from './formant.js';

(function() {
  "use strict";

  const html = $n.e('div', {"class":"uk-alert-danger", "uk-alert": ""},
                    $n.e('a', {"class": "uk-alert-close", "uk-close": ""}),
                    $n.e('p'));
  //console.log(html.outerHTML);

  // utils
  const $get = (id) => { return document.getElementById(id); }
  const $getClass = (name) => {return document.getElementsByClassName(name); }
  const $select = (key) => { return document.querySelector(key); }
  const $selectAll = (key) => { return document.querySelectorAll(key); }
  const $create = (tag) => { return document.createElement(tag); }
  const $show = (id) => { document.getElementById(id).removeAttribute('hidden'); }
  const $hide = (id) => { document.getElementById(id).setAttribute('hidden', ''); }
  const $replaceQueryString = (search) => { history.replaceState(null, '', `${window.location.origin}${window.location.pathname}?${search}`); };

  /*
  let match = window.location.pathname.match(/^\/(en|zh)\/(.*)/)
  if (match) {
    if (match[1] === 'en') {
      TERM_LABELS = TERM_LABELS_EN
      locale = 'en'
    } else if (match[1] === 'zh') {
      TERM_LABELS = TERM_LABELS_ZH
    }
  }
  */

  //console.log(TERM_LABELS, match[1] === 'en', locale);

  // global state
  const state = {
    results: {},
    resultsView: 'table',
    resultsChecklist: {},
    resultsMap: {},
    map: null,
    mapMarkers: [],
  };
  const ACCEPTED_VIEWS = ['table', 'list', 'map', 'gallery', 'checklist'];

  // selector
  const searchbarDropdown = $get('de-searchbar__dropdown');
  const searchbarInput = $get('de-searchbar__input');
  const searchbarDropdownList = $get('de-searchbar__dropdown__list');
  const tokenList = $get('de-tokens');
  const submitButton = $get('de-submit-button');
  const resultsTBody = document.getElementById('phok-results-tbody');

  // # init
  const init = () => {
    // ## parse query string
    /*
    const params = new URLSearchParams(document.location.search);
    const filterParams = {};
    params.forEach((value, term) => {
      if (term === 'view' && ACCEPTED_VIEWS.includes(value)) {
        state.resultsView = value;
      } else if (Object.keys(TERM_LABELS).includes(term)) {
        if (term === 'collector') {
          filterParams[term] = [value];
        } else {
          filterParams[term] = value;
        }
      } else
        filterParams[term] = value;
      {}
    });

    console.log('init', filterParams);
    if (Object.keys(filterParams).length > 0) {
      myFilter.fromParams(filterParams)
              .then( x => {
                // console.log(x);
                refreshTokens();
                // auto do search
                exploreData();
              })
    }
    */
    // apply result view type click event
    let children = $select('#de-result-view-tab').childNodes
    for (const node of children) {
      if (node.nodeName === 'LI') {
        //console.log(node, node.nodeType, node.nodeName);
        if (state.resultsView === node.dataset.view) {
          UIkit.tab('#de-result-view-tab').show(node.dataset.tab);
        }
        node.onclick = (e) => {
        e.preventDefault();
          e.stopPropagation();
          const item = e.currentTarget;
          state.resultsView = item.dataset.view;
          UIkit.tab('#de-result-view-tab').show(item.dataset.tab);
          if (['table', 'list', 'gallery'].includes(state.resultsView)) {
            if (state.results && state.results.data) {
              refreshResult();
            } else {
              exploreData();
            }
          } else if (state.resultsView === 'map') {
            if (state.resultsMap && state.resultsMap.data) {
              refreshResult();
            } else {
              exploreData();
            }
          } else if (state.resultsView === 'checklist') {
            if (state.resultsChecklist && state.resultsChecklist.data) {
              refreshResult();
            } else {
              exploreData();
            }
          }
        }
      }
    }
  }

  const resultsTitle = document.getElementById('phok-results-title');


  /******* Formant: Form Module *******/
  const formantOptions = {
    selectCallbacks: {
      taxon_id: (element, options) => {
        element[0] = new Option('-- choose --', '', true, true);
        options.forEach( (v, i) => {
          let text = v.full_scientific_name;
          if (v.common_name) {
            text = `${text} (${v.common_name})`;
          }
          element[i+1] = new Option(text, v.id, false);
        });
      },
      collector_input__exclude: (entity, options, args) => {
        const autocompleteInput = document.getElementById('form-collector');
        const dropdownList = document.getElementById('form-collector__dropdown');
        const targetInput = document.getElementById('form-collector_id');

        dropdownList.innerHTML = '';
        console.log(options);
        options.forEach( v => {
          let choice = document.createElement('li');
          choice.classList.add('uk-flex', 'uk-flex-between');
          let display = `${v.full_name_en} ${v.full_name}`;
          choice.dataset.display = display;
          choice.dataset.pid = v.id;
          choice.innerHTML = `
            <div class="uk-padding-small uk-padding-remove-vertical">${display}</div>
            <div class="uk-padding-small uk-padding-remove-vertical uk-text-muted">${v.abbreviated_name}</div>`;
          choice.onclick = (e) => {
            dropdownList.setAttribute('hidden', '');
            autocompleteInput.value = e.currentTarget.dataset['display'];
            targetInput.value = e.currentTarget.dataset['pid'];
          }
          dropdownList.appendChild(choice);
        });
      }
    }
  };
  Formant.register('adv-search-form');
  Formant.setHelpers('fetch', fetchData);
  Formant.setOptions(formantOptions);

  const collectorInputClear = $get('form-collector__clear');
  collectorInputClear.onclick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const autocompleteInput = document.getElementById('form-collector');
    const targetInput = document.getElementById('form-collector_id');
    autocompleteInput.value = '';
    targetInput.value = '';
  };

  // begin sort nav
  let sortFilter = {'field_number': 'asc'};
  const $sortNavItems = document.getElementsByClassName('sort-nav')
  const $sortNavLabel = document.getElementById('sort-nav-label')
  for (let nav of $sortNavItems) {
    nav.onclick = (e) => {
      e.preventDefault()
      $sortNavLabel.innerHTML = `Sort: ${e.target.innerHTML}`
      UIkit.dropdown('#sort-select').hide(false)
      if (e.target.dataset.desc === '1') {
        sortFilter = {[e.target.dataset.sort]: 'desc'}
      } else {
        sortFilter = {[e.target.dataset.sort]: 'asc'}
      }
      exploreData()
    }
  }

  const goSearch = () => {
    $show('de-loading');
    $hide('toggle-adv-search');
    let filters = Formant.getFilterSet();
    let page_range = myPagination.getRange();
    console.log(page_range);
    const url = `/api/v1/search?filter=${JSON.stringify(filters)}&range=${JSON.stringify(page_range)}`;
    fetchData(url)
      .then( resp => {
        console.log('goSearch', resp);
        $hide('de-loading');
        $show('de-results-container');
        myPagination.setPageCount(resp.total);
        state.resultView = 'table';
        state.results = resp;

        //console.log(state.results);
        refreshResult();
        tokenList.innerHTML = '';
        Formant.getTokens(filters)
               .then( tokens => {
                 // create tokens
                 for (const t of tokens) {
                   let token = $create('div');
                   let card = $create('div');
                   card.className = 'uk-card de-token uk-border-rounded';
                   let flex = $create('div');
                   flex.className = 'uk-flex uk-flex-middle';
                   let content = $create('div');
                   content.innerHTML = `<span class="uk-label uk-label-success">${t.label}</span> = ${(t.displayValue) ? t.displayValue : t.value}</div>`;
                   let btn = $create('button');
                   btn.type = 'button';
                   btn.classList.add('uk-margin-left');
                   btn.setAttribute('uk-close', '');
                   btn.onclick = (e) => {
                     //removeFilter(e, v)
                     Formant.removeFilter(t.key);
                     goSearch();
                   };
                   flex.appendChild(content);
                   flex.appendChild(btn);
                   card.appendChild(flex);
                   token.appendChild(card);
                   tokenList.appendChild(token);
                 }
               })
      })
      .catch( error => {
        alert(error);
      })
  }

  const removeFilter = ((e, token) => {
    e.preventDefault();
    e.stopPropagation();
    //formData.delete(key)
    console.log('close', token[0] )
    switch(token[0]) {
      case 'queryTaxon':
        let queryTaxonInput = $get('form-scientificName');
        queryTaxonInput.value = '';
      case 'taxon':
        let ElementList = document.getElementsByClassName('hast-taxon');
        for (let i = 0; i < ElementList.length; i++) {
          console.log(ElementList[i].value, token[1]);
          if (parseInt(token[1]) === parseInt(ElementList[i].value)) {
            ElementList[i].value = '';
          }
        }
        break;
      case 'collector':
        collectorInput.value = '';
        collectorInputId.value = '';
        break;
      case 'fieldNumber':
        let fieldNumberInput = $get('form-fieldNumber');
        let fieldNumberInput2 = $get('form-fieldNumber2');
        fieldNumberInput.value = '';
        fieldNumberInput2.value = '';
        break;
      case 'collect_date':
        let collectDateInput = $get('form-collectDate');
        let collectDate2Input = $get('form-collectDate2');
        collectDateInput.value = '';
        collectDateInput2.value = '';
      case 'collectMonth':
        let collectMonthInput = $get('form-collectMonth');
        collectMonthInput.value = '';
      case 'namedAreaId':
        let naList = document.getElementsByClassName('hast-named-area');
        for (let i = 0; i < naList.length; i++) {
          if (parseInt(token[1]) === parseInt(naList[i].value)) {
            naList[i].value = '';
          }
        }
        break;
      case 'queryLocality':
        let queryLocalityInput = $get('form-locality_text');
        queryLocalityInput.value = '';
        break;
      case 'altitude':
        break;
      case 'accessionNumber':
        break;
      case 'typeStatus':
        break;
      default:
        break;
    }
    //doSearch();
  });

  const SearchSubmit = $get('search-submit');
  SearchSubmit.onclick = (e) => {
    e.preventDefault();
    goSearch();
  }

  // end sort nav



  const myResults = (() => {
    const pub = {};
    let view = 'table';
    let results = {};
    let resultsMap = {};
    let resultsChecklist = {};
    let map = {};
    let mapMarkers = {};

    pub.init = () => {}
    return pub;
  })();
  myResults.init();

  const myPagination = (() => {
    let current = 1;
    let pageCount = 1;
    let pageSize = 20;
    let container = null;

    const pub = {};
    pub.init = (elementId) => {
      container = document.getElementById(elementId);
    }
    pub.render = (count) => {
      container.innerHTML = '';

      for(let i=1; i<=pageCount; i++) {
        let item = $create('li');
        if (i === current) {
          item.classList.add('uk-active');
        }
        let link = $create('a');
        link.setAttribute('href', '#');
        link.onclick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          current = parseInt(e.target.innerHTML, 10);
          //exploreData();
          goSearch();
        }
        link.innerHTML = i;
        item.appendChild(link);
        container.appendChild(item);
      }
    }
    pub.getRange = () => {
      return [(current-1) * pageSize, current*pageSize];
    }
    pub.setPageCount = (total) => {
      pageCount = Math.ceil(total / pageSize) || 1;
      return pageCount;
    }
    return pub;
  })();
  myPagination.init('de-pagination');

  /*
   * <Searchbar>
   */
  const renderSearchbarDropdownItems = (data) => {
    // clear
    searchbarDropdownList.innerHTML = '';
    const fd = Formant.getFormData();

    const handleItemClick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      //e.stopImmediatePropagation();
      // console.log(e.target, e.currentTarget);
      const selectedIndex = e.currentTarget.dataset['key'];
      //UIkit.dropdown(DROPDOWN_ID).hide(false);
      const selectedData = data[selectedIndex];
      const term = selectedData.meta.term;
      console.log(term, selectedData);
      showSearchbarDropdown(false)
      if (term === 'field_number_with_collector') {
        Formant.addFilter('collector_id', selectedData.collector.id);
        Formant.addFilter('collector_input__exclude', selectedData.collector.display_name);
        Formant.addFilter('field_number', selectedData.field_number);
      } else if (term === 'field_number') {
        Formant.addFilter('field_number', selectedData.field_number);
      } else if (term === 'collector') {
        Formant.addFilter('collector_id', selectedData.id);
        Formant.addFilter('collector_input__exclude', selectedData.display_name);
      } else if (term === 'taxon') {
        const familySelect = document.getElementById('form-family');
        const genusSelect = document.getElementById('form-genus');
        const speciesSelect = document.getElementById('form-species');

        $show('de-loading');
        fetchData(`/api/v1/taxa/${selectedData.id}?children=1`)
          .then( resp=> {
            switch(selectedData.rank) {
              case 'species':
                //console.log(data[selectedIndex]);
                familySelect.value = resp.higher_taxon[1].id;
                for (const i in resp.genus) {
                  const v = resp.genus[i];
                  if (parseInt(v.id) === parseInt(resp.higher_taxon[0].id)) {
                    genusSelect[i] = new Option(v.display_name, v.id, true, true);
                  } else {
                    genusSelect[i] = new Option(v.display_name, v.id, false);
                  }
                }
                for (const i in resp.species) {
                  const v = resp.species[i];
                  if (parseInt(v.id) === parseInt(selectedData.id)) {
                    speciesSelect[i] = new Option(v.display_name, v.id, true, true);
                  } else {
                    speciesSelect[i] = new Option(v.display_name, v.id, false);
                  }
                }
                break;
              case 'genus':
                familySelect.value = resp.higher_taxon[0].id;
                //fam.dispatchEvent(new Event('change'));
                for (const i in resp.genus) {
                  const v = resp.genus[i];
                  if (parseInt(v.id) === parseInt(selectedData.id)) {
                    genusSelect[i] = new Option(v.display_name, v.id, true, true);
                  } else {
                    genusSelect[i] = new Option(v.display_name, v.id, false);
                  }
                }
                speciesSelect[0] = new Option('-- choose --', '', true, true);
                let j = 1;
                for (const i in resp.species) {
                  const v = resp.species[i];
                  speciesSelect[j++] = new Option(v.display_name, v.id, false);
                }
                break;
              case 'family':
                familySelect.value = selectedData.id;
                break;
              default:
                console.log('TODO searchbar not support this rank');
            }
            searchbarInput.value = '';
            goSearch();
            return;
          });
        //Formant.addFilter('taxon_id', data[selectedIndex].id, groupIndex);
      } else {
        Formant.addFilter(term, data[selectedIndex].value);
      }

      searchbarInput.value = '';
      goSearch();
    }

    data.forEach((item, index) => {
      const { label, display } = item.meta;
      let choice = document.createElement('li');
      choice.addEventListener('click', handleItemClick, true);
      choice.dataset.key = index;
      choice.classList.add('uk-flex', 'uk-flex-between');
      choice.innerHTML = `
        <div class="uk-padding-small uk-padding-remove-vertical">${display}</div>
        <div class="uk-padding-small uk-padding-remove-vertical uk-text-muted">${label}</div>`;
      searchbarDropdownList.appendChild(choice);
    });
  }

  const showSearchbarDropdown = (isShow) => {
    if (isShow === true) {
      searchbarDropdown.removeAttribute('hidden')
    } else {
      searchbarDropdown.setAttribute('hidden', '')
    }
  }

  const handleInput = (e) => {
    const q = e.target.value;
    //console.log(q, 'inpu');
    if (q.length > 0) {
      const endpoint = `/api/v1/searchbar?q=${q}`;
      fetchData(endpoint)
        .then( resp => {
          if (resp.data.length > 0) {
            searchbarInput.classList.remove('uk-form-danger')
            renderSearchbarDropdownItems(resp.data);
          } else {
            searchbarInput.classList.add('uk-form-danger')
          }
        })
        .catch( error => {
          console.log(error);
        });
    } else {
      //UIkit.dropdown(DROPDOWN_ID).hide(false);
    }
  }

  const handleFocus = (e) => {
    //UIkit.dropdown(DROPDOWN_ID).hide(false); // I don't need dropdown behavier (hover show)
    showSearchbarDropdown(true)
  }

  const handleBlur = (e) => {
    // delay hide dropdown wait if click on item

    setTimeout(() => {
      showSearchbarDropdown(false)
    }, 200)

  }

  // bind input event
  searchbarInput.addEventListener('input', handleInput)
  searchbarInput.addEventListener('focus', handleFocus)
  // searchbarInput.addEventListener('focusout', handleFocusout)
  searchbarInput.addEventListener('blur', handleBlur)


  const refreshResult = () => {
    let results = state.results;
    const view = state.resultsView;
    const resultsViewList = document.getElementsByClassName('data-explore-result-view');
    // show 1 result
    for (let i = 0; i < resultsViewList.length; i++) {
      resultsViewList[i].setAttribute('hidden', '');
      if (resultsViewList[i].dataset.view === view) {
        const resultWrapper = $get(`data-explore-result-${view}`);
        resultWrapper.removeAttribute('hidden');
      }
    }

    if (['table', 'list', 'gallery'].includes(view)) {
      resultsTitle.innerHTML = `筆數: ${results.total.toLocaleString()} <span class="uk-text-muted uk-text-small">(${results.elapsed.toFixed(2)} 秒)</span>`;
      $show('de-pagination');
      myPagination.render()
    } else {
      $hide('de-pagination');
    }

    switch(view) {
      case 'table':
        renderResultTable(results);
        break;
      case 'gallery':
        renderResultGallery(results);
        break;
      case 'list':
        renderResultList(results);
        break;
      case 'map':
        renderResultMap();
        break;
      case 'checklist':
        renderResultChecklist();
        break;
      default:
        break;
    }
  }
  const renderResultChecklist = () => {
    const c = $get('data-explore-result-checklist');
    let family = '';
    state.resultsChecklist.data.forEach( x => {
      if (x.children.length > 0) {
        let genus = '';
        x.children.forEach( y => {
          if (y.children.length > 0) {
            let species = '';
            y.children.forEach( z => {
            species += `<li>${z.obj.display_name} <span class="uk-badge">${z.count}</span></li>`;
            });
            genus += `<li>${y.obj.display_name} <span class="uk-badge">${y.count}</span><ul class="uk-list uk-list-square">${species}</ul></li>`;
          }
        });
        family += `<li>${x.obj.display_name} <span class="uk-badge">${x.count}</span><ul class="uk-list uk-list-circle">${genus}</ul></li>`;
      } else {
        family += `<li>${x.obj.display_name} <span class="uk-badge">${x.count}</span></li>`;
      }
    })
    c.innerHTML = `<ul class="uk-list uk-list-disc">${family}</ul>`;
  }

  const renderResultMap = () => {
    if (state.map === null) {
      state.map = L.map('data-explore-result-map').setView([23.181, 121.932], 7);
      const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      }).addTo(state.map);
    }

    for(let i=0; i<state.mapMarkers.length; i++) {
      state.map.removeLayer(state.mapMarkers[i]);
    }

    state.resultsMap.data.forEach( (x) => {
      const html = `<div>館號: ${x.accession_number}</div><div>採集者:${x.collector.display_name}</div><div>採集號: ${x.field_number}</div><div>採集日期: ${x.collect_date}</div><div><a href="/specimens/HAST:${x.accession_number}" target="_blank">查看</a></div>`;
      const marker = L
        .marker([parseFloat(x.latitude_decimal), parseFloat(x.longitude_decimal)])
        //.addTo(state.map)
	.bindPopup(html)
        .openPopup();
      state.map.addLayer(marker);
      state.mapMarkers.push(marker);
    });
  }

  const renderResultList = (results) => {
    const resultContainer = $get('data-explore-result-list');
    resultContainer.innerHTML = '';
    results.data.forEach( x => {
      const collector = (x.collector) ? x.collector.display_name : '';
      const namedAreas = x.named_areas.map(na => na.display_name).join(', ');

      let wrapper = $create('div');
      wrapper.setAttribute('uk-grid', '');
      const img = `<img src="${x.image_url.replace('_s', '_m')}" width="150", alt="Specimen Image">`
      const link = renderDetailLink(img, x.accession_number)

      const info = `<p class="uk-text-large uk-margin-remove-bottom">${x.taxon_text}</p>
           <p class="uk-text-muted uk-margin-remove-top">
            <b>館號:</b> ${x.accession_number}<br />
            <b>採集者/採集號:</b> ${collector} ${x.field_number}<br />
            <b>採集日期:</b> ${x.collect_date}<br />
            <b>採集地:</b> ${namedAreas}</p>`
      const link2 = renderDetailLink(info, x.accession_number)
      wrapper.innerHTML = `
        <div class="uk-width-1-5">
          ${link}
        </div>
        <div class="uk-width-expand">
          ${link2}
        </div>
      `;
      resultContainer.appendChild(wrapper);
    });
  }

  const renderResultGallery = (results) => {
    const resultContainer = $get('data-explore-result-gallery');
    resultContainer.innerHTML = '';
    results.data.forEach( x => {
      const imageKey = `data-explore-result-gallery-image-${x.record_key}`;
      const domString = `
      <div>
        <div class="uk-card uk-card-default">
            <div class="uk-card-media-top" id="${imageKey}">
                PUT IMAGE HERE
            </div>
            <div class="uk-card-body">
                <h3 class="uk-card-title">館號: ${x.accession_number}</h3>
<dl class="uk-description-list">
    <dt>學名</dt>
    <dd>${x.proxy_taxon_scientific_name}</dd>
    <dt>採集號</dt>
    <dd>${x.collect_num}</dd>
</dl>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt.</p>
            </div>
        </div>
    </div>`;
      const doc = new DOMParser().parseFromString(domString, 'text/xml');
      resultContainer.appendChild(doc.firstChild)

      // add image
      const imageWrapper = $get(imageKey);
      imageWrapper.innerHTML = '';
      console.log(imageWrapper, imageKey);
      if (x.image_url) {
        let imgElem = document.createElement('img');
        imgElem.setAttribute('src', x.image_url.replace('_s', '_m'));
        imgElem.setAttribute('width', '1800');
        imgElem.setAttribute('height', '1200');
        // TODO: alt
        imageWrapper.appendChild(imgElem);
      }
    });
    resultContainer.removeAttribute('hidden');
  }

  const renderDetailLink = (content, id) => {
    return `<a class="uk-link-reset" href="/specimens/HAST:${id}">${content}</a>`;
  };

  const renderResultTable = (results) => {
    resultsTBody.innerHTML = '';

    results.data.forEach(item => {
      const namedAreas = item.named_areas.map(x => x.name);

      const row = document.createElement('tr');
      let col1 = document.createElement('td');
      let chk = document.createElement('input');
      chk.type = 'checkbox';
      /*
      chk.classList.add('uk-checkbox');
      if (storeRecordsSet.has(item.record_key)) {
        chk.checked = true;
      }
      chk.onchange = (e) => {
        //console.log(e, e.target.value, e.target.checked, e.currentTarget.value, item.record_key);
        if (storeRecordsSet.has(item.record_key)) {
          storeRecordsSet.delete(item.record_key)
        } else {
          storeRecordsSet.add(item.record_key);
        }
        localStorage.setItem('store-records', JSON.stringify(Array.from(storeRecordsSet)));
        printButton.innerHTML = `Print (${storeRecordsSet.size})`;
      }
      */
      col1.appendChild(chk);
      let col2 = document.createElement('td');
      col2.classList.add('uk-table-link');
      let tmp = (item.image_url) ? `<img class="uk-preserve-width uk-border-rounded" src="${item.image_url}" width="40" height="40" alt="">` : '';
      col2.innerHTML = renderDetailLink(tmp, item.accession_number);
      let col3 = document.createElement('td');
      col3.classList.add('uk-table-link');
      tmp = item.accession_number || '';
      col3.innerHTML = renderDetailLink(tmp, item.accession_number);
      let col99 = document.createElement('td');
      col99.classList.add('uk-table-link');
      tmp = item.type_status.charAt(0).toUpperCase() + item.type_status.slice(1);
      col99.innerHTML = renderDetailLink(tmp, item.accession_number);
      let col4 = document.createElement('td');
      col4.classList.add('uk-table-link');
      tmp = `${item.taxon_text}`;
      col4.innerHTML = renderDetailLink(tmp, item.accession_number);
      let col5 = document.createElement('td');
      col5.classList.add('uk-table-link');
      tmp = (item.collector) ? `${item.collector.display_name} <span class="uk-text-bold">${item.field_number}</span>` : `<span class="uk-text-bold">${item.field_number}</span>`;
      col5.innerHTML = renderDetailLink(tmp, item.accession_number);
      let col6 = document.createElement('td');
      tmp = item.collect_date;
      col6.innerHTML = renderDetailLink(tmp, item.accession_number);
      col6.classList.add('uk-table-link');
      let col7 = document.createElement('td');
      col7.innerHTML = namedAreas.join('/') + '<a href="#offcanvas-usage" uk-toggle>Open</a>';
      col7.classList.add('uk-table-link');
      row.appendChild(col1);
      row.appendChild(col2);
      row.appendChild(col3);
      row.appendChild(col99);
      row.appendChild(col4);
      row.appendChild(col5);
      row.appendChild(col6);
      row.appendChild(col7);
      resultsTBody.appendChild(row);
    });
  };

  submitButton.onclick = (e) => {
    e.preventDefault();
    goSearch();
  };

  init();
})();
