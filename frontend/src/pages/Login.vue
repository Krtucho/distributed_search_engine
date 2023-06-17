<template>
  <div >
    <q-layout view="lHh lpr lFf"  class="shadow-2 rounded-borders">
      <!-- <q-header elevated>
        <q-toolbar>
          <q-btn flat round dense icon="menu" class="q-mr-sm" />
          <q-avatar>
            <img src="https://cdn.quasar.dev/logo-v2/svg/logo-mono-white.svg">
          </q-avatar> 

          <q-toolbar-title>Catálogo de juegos</q-toolbar-title>

          <q-btn flat round dense icon="whatshot" />
        </q-toolbar>
      </q-header> -->

      <div >
          <div class="row justify-center" >
            <!-- <div class="col-12 col-md-auto" style="padding-top: 8%;">
              <div class="text-h2" style="font-weight: bold; color: #43AAFF; font-size: 1.6em;"> Listado de Juegos de XBOX 360</div>
            </div> -->
            <!-- <div class="col-12 justify-content-center">
              <q-checkbox  dark keep-color v-model="showPictures" label="Mostrar imágenes" color="cyan" />
            </div> -->
           
            <div v-if="!didSearch"  class="col-12 q-mt-xl" style="margin-top:15%; ">
              <div class="row justify-center">
                <!-- <h1 class="col-12">
                  Krtucho's Search Engine
                </h1>
               -->
                <div class="col-8" style="width:100px; height:100px;">
                  <img class="row img-background q-py-sm" src="assets/img/descarga.png">
                </div>
              </div>
            </div>

            
             
            <div class="col-8">
              
              <form class="row q-pt-sm form-inline" v-on:submit.prevent="buscarCoctel()">
                <q-input  dense standout outlined type="text" class="col-12 form-control mr-2 q-pb-sm" placeholder="Search" v-model="nombreCoctel"/>
                
                <div class="col-12">
                 <div class="row justify-center">
                   <q-select class="col" borderless v-model="nombreCoctel" :options="queryOptions" label="Select Default Query"  style="max-width:15em;"/>
                    <q-select class="col-4 q-pr-sm" borderless v-model="model" :options="options" label="Select Model"  style="max-width:8.5em;"/>
                     <q-select class="col-4 q-pr-sm" borderless v-model="dataBase" :options="dataOptions" label="Select DataBase"  style="max-width:10.5em;"/>
                    <button class="col-4 btn btn-primary q-pl-sm search-bt" style="max-width:5em;">
                      Search
                    </button>
                  </div>

                  <div class="row">
                    
                  </div>

                  <!-- <q-select
                    filled
                    :value="model"
                    use-input
                    hide-selected
                    fill-input
                    hide-dropdown-icon
                    input-debounce="0"
                    :options="qoptions"
                    @filter="filterFn"
                    style="width: 250px; padding-bottom: 32px"
                    @click.capture.native="onClick"
                    @input-value="onInputValue"
                    @popup-hide="onPopupHide"
                    @popup-show="onPopupShow"
                  >
                    <template v-slot:before-options >
                      <q-tabs
                        v-model="tab"
                        class="bg-teal text-yellow"
                        style="position: sticky;top: 0px; z-index: 1;"
                      >
                        <q-tab name="mails" icon="mail" />
                      </q-tabs>
                    </template>
                    <template v-slot:no-option>
                      <q-item>
                        <q-item-section class="text-grey">
                          No results
                        </q-item-section>
                      </q-item>
                    </template>
                  </q-select> -->
                </div>
               
                
              </form>
            </div>
          </div>
        
        <div v-if="didSearch" class="row justify-center" style="padding-bottom: 10%; padding-top: 1%;">
          <div class="row justify-center" style="width: 60%;"> 
            <q-list bordered separator v-for="(game, index) in getData" :key="index" class="col-12">              
              <q-item clickable v-ripple class="column"  :href="game.url">
                        <!-- <q-item-img class="col">
                          <img v-if="showPictures" img v-bind:src="game.img" alt="Generic placeholder image" width="200" class="ml-lg-5 order-1 order-lg-2" />
                        </q-item-img> -->
                        <q-item-label class="col"> {{ game.name }} | {{ index }}</q-item-label>
                        <q-item-label caption class="col" v-bind:href="game.url"> {{ game.url }}</q-item-label>
                        
              </q-item>
      
            </q-list>
              <div class="column col-12 items-center">
                    <q-pagination
                          v-model="page"
                          :min="currentPage" 
                          :max="Math.ceil(gamesList.length/totalPages)"
                          :input="true"
                          input-class="text-orange-10"
                    >
                    </q-pagination>
              </div>
          </div>
        </div>
      </div>

      <!-- <q-footer elevated >
        <q-toolbar >
          <q-toolbar-title>Como contactárnos</q-toolbar-title>

          <q-space />


          <q-icon color="accent" size="2rem" style="padding-right: 1%;">
            <a href="https://t.me/VentadeJuegosCubaCanal">
              <svg xmlns="http://www.w3.org/2000/svg"  viewBox="0 0 48 48" width="48px" height="48px"><path fill="#29b6f6" d="M24 4A20 20 0 1 0 24 44A20 20 0 1 0 24 4Z"/><path fill="#fff" d="M33.95,15l-3.746,19.126c0,0-0.161,0.874-1.245,0.874c-0.576,0-0.873-0.274-0.873-0.274l-8.114-6.733 l-3.97-2.001l-5.095-1.355c0,0-0.907-0.262-0.907-1.012c0-0.625,0.933-0.923,0.933-0.923l21.316-8.468 c-0.001-0.001,0.651-0.235,1.126-0.234C33.667,14,34,14.125,34,14.5C34,14.75,33.95,15,33.95,15z"/><path fill="#b0bec5" d="M23,30.505l-3.426,3.374c0,0-0.149,0.115-0.348,0.12c-0.069,0.002-0.143-0.009-0.219-0.043 l0.964-5.965L23,30.505z"/><path fill="#cfd8dc" d="M29.897,18.196c-0.169-0.22-0.481-0.26-0.701-0.093L16,26c0,0,2.106,5.892,2.427,6.912 c0.322,1.021,0.58,1.045,0.58,1.045l0.964-5.965l9.832-9.096C30.023,18.729,30.064,18.416,29.897,18.196z"/></svg>        
            </a>
          </q-icon>

          <q-icon color="accent" size="2rem">
            <a href="https://chat.whatsapp.com/Ixc6EAtouCX59gyNnKEBvU">
              <svg xmlns="http://www.w3.org/2000/svg"  viewBox="0 0 48 48" width="48px" height="48px" fill-rule="evenodd" clip-rule="evenodd"><path fill="#fff" d="M4.868,43.303l2.694-9.835C5.9,30.59,5.026,27.324,5.027,23.979C5.032,13.514,13.548,5,24.014,5c5.079,0.002,9.845,1.979,13.43,5.566c3.584,3.588,5.558,8.356,5.556,13.428c-0.004,10.465-8.522,18.98-18.986,18.98c-0.001,0,0,0,0,0h-0.008c-3.177-0.001-6.3-0.798-9.073-2.311L4.868,43.303z"/><path fill="#fff" d="M4.868,43.803c-0.132,0-0.26-0.052-0.355-0.148c-0.125-0.127-0.174-0.312-0.127-0.483l2.639-9.636c-1.636-2.906-2.499-6.206-2.497-9.556C4.532,13.238,13.273,4.5,24.014,4.5c5.21,0.002,10.105,2.031,13.784,5.713c3.679,3.683,5.704,8.577,5.702,13.781c-0.004,10.741-8.746,19.48-19.486,19.48c-3.189-0.001-6.344-0.788-9.144-2.277l-9.875,2.589C4.953,43.798,4.911,43.803,4.868,43.803z"/><path fill="#cfd8dc" d="M24.014,5c5.079,0.002,9.845,1.979,13.43,5.566c3.584,3.588,5.558,8.356,5.556,13.428c-0.004,10.465-8.522,18.98-18.986,18.98h-0.008c-3.177-0.001-6.3-0.798-9.073-2.311L4.868,43.303l2.694-9.835C5.9,30.59,5.026,27.324,5.027,23.979C5.032,13.514,13.548,5,24.014,5 M24.014,42.974C24.014,42.974,24.014,42.974,24.014,42.974C24.014,42.974,24.014,42.974,24.014,42.974 M24.014,42.974C24.014,42.974,24.014,42.974,24.014,42.974C24.014,42.974,24.014,42.974,24.014,42.974 M24.014,4C24.014,4,24.014,4,24.014,4C12.998,4,4.032,12.962,4.027,23.979c-0.001,3.367,0.849,6.685,2.461,9.622l-2.585,9.439c-0.094,0.345,0.002,0.713,0.254,0.967c0.19,0.192,0.447,0.297,0.711,0.297c0.085,0,0.17-0.011,0.254-0.033l9.687-2.54c2.828,1.468,5.998,2.243,9.197,2.244c11.024,0,19.99-8.963,19.995-19.98c0.002-5.339-2.075-10.359-5.848-14.135C34.378,6.083,29.357,4.002,24.014,4L24.014,4z"/><path fill="#40c351" d="M35.176,12.832c-2.98-2.982-6.941-4.625-11.157-4.626c-8.704,0-15.783,7.076-15.787,15.774c-0.001,2.981,0.833,5.883,2.413,8.396l0.376,0.597l-1.595,5.821l5.973-1.566l0.577,0.342c2.422,1.438,5.2,2.198,8.032,2.199h0.006c8.698,0,15.777-7.077,15.78-15.776C39.795,19.778,38.156,15.814,35.176,12.832z"/><path fill="#fff" fill-rule="evenodd" d="M19.268,16.045c-0.355-0.79-0.729-0.806-1.068-0.82c-0.277-0.012-0.593-0.011-0.909-0.011c-0.316,0-0.83,0.119-1.265,0.594c-0.435,0.475-1.661,1.622-1.661,3.956c0,2.334,1.7,4.59,1.937,4.906c0.237,0.316,3.282,5.259,8.104,7.161c4.007,1.58,4.823,1.266,5.693,1.187c0.87-0.079,2.807-1.147,3.202-2.255c0.395-1.108,0.395-2.057,0.277-2.255c-0.119-0.198-0.435-0.316-0.909-0.554s-2.807-1.385-3.242-1.543c-0.435-0.158-0.751-0.237-1.068,0.238c-0.316,0.474-1.225,1.543-1.502,1.859c-0.277,0.317-0.554,0.357-1.028,0.119c-0.474-0.238-2.002-0.738-3.815-2.354c-1.41-1.257-2.362-2.81-2.639-3.285c-0.277-0.474-0.03-0.731,0.208-0.968c0.213-0.213,0.474-0.554,0.712-0.831c0.237-0.277,0.316-0.475,0.474-0.791c0.158-0.317,0.079-0.594-0.04-0.831C20.612,19.329,19.69,16.983,19.268,16.045z" clip-rule="evenodd"/></svg>
            </a>
          </q-icon>
        </q-toolbar>
      </q-footer> -->

      <!-- <q-page-container>
        <q-page class="q-pa-md">
          <p v-for="n in 2" :key="n">
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Fugit nihil praesentium molestias a adipisci, dolore vitae odit, quidem consequatur optio voluptates asperiores pariatur eos numquam rerum delectus commodi perferendis voluptate?
          </p>
        </q-page>
      </q-page-container> -->
    </q-layout>
  </div>
</template>

 <!-- <div v-if="bebidas != null">
        <div class="row">
        <div class="col-lg-8 mx-auto">
            
            <paginate  class="list-group shadow" ref="paginator" name="bebidas" :list="bebidas" :per="3">
            
            <li class="list-group-item" v-for="bebida in paginated('bebidas')" :key="bebida.idDrink">
                
                <div class="media align-items-lg-center flex-column flex-lg-row p-3" >
                <div class="media-body order-2 order-lg-1">
                    <h5 class="mt-0 font-weight-bold mb-2">{{ bebida.strDrink }}</h5>
                    <p class="font-italic text-muted mb-0 small"> {{ bebida.strCategory }} | {{ bebida.strAlcoholic }} | {{ bebida.strGlass }}</p>
                    <p>{{ bebida.strInstructions }}</p>
                </div>
                <img :src="bebida.strDrinkThumb" alt="Generic placeholder image" width="200" class="ml-lg-5 order-1 order-lg-2" />
                </div>
                
            </li>
            
            </paginate>
        
        </div>
        </div>
        <div class="d-flex justify-content-center mt-4">
            <paginate-links :classes="{ ul: 'pagination', li: 'page-item', a: 'page-link' }" for="bebidas" :show-step-links="true" :limit="2" :async="true"></paginate-links>
        </div>
    </div>
    <div v-else>
        <h2 class="display-5 text-center">Sin resultados</h2>
    </div> -->

<script>
import axios from "axios";
import { defineComponent } from 'vue';
import { ref } from 'vue'

// import { env } from 'process'
// import process from 'process/browser';

// import VuePaginate from "vue-paginate";
// Vue.component("paginate", VuePaginate);

const default_queries = [
  'what similarity laws must be obeyed when constructing aeroelastic models\nof heated high speed aircraft .', 
  'what are the structural and aeroelastic problems associated with flight\nof high speed aircraft .', 
  'what problems of heat conduction in composite slabs have been solved so\nfar .', 
  'can a criterion be developed to show empirically the validity of flow\nsolutions for chemically reacting gas mixtures based on the simplifying\nassumption of instantaneous local chemical equilibrium .\n', 
  'what chemical kinetic system is applicable to hypersonic aerodynamic\nproblems .\n', 
  'what theoretical and experimental guides do we have as to turbulent\ncouette flow behaviour .\n', 
  'is it possible to relate the available pressure distributions for an\nogive forebody at zero angle of attack to the lower surface pressures of\nan equivalent ogive forebody at angle of attack .\n', 
  'what methods -dash exact or approximate -dash are presently available\nfor predicting body pressures at angle of attack.\n', 
  'papers on internal /slip flow/ heat transfer studies .\n', 
  'are real-gas transport properties for air available over a wide range of\nenthalpies and densities .\n', 
  'is it possible to find an analytical,  similar solution of the strong\nblast wave problem in the newtonian approximation .\n', 
  'how can the aerodynamic performance of channel flow ground effect\nmachines be calculated .\n', 
  'what is the basic mechanism of the transonic aileron buzz .\n', 
  'papers on shock-sound wave interaction .\n', 
  'material properties of photoelastic materials .\n', 
  'can the transverse potential flow about a body of revolution be\ncalculated efficiently by an electronic computer .\n', 
  'can the three-dimensional problem of a transverse potential flow about\na body of revolution be reduced to a two-dimensional problem .\n', 
  'are experimental pressure distributions on bodies of revolution at angle\nof attack available .\n', 
  'does there exist a good basic treatment of the dynamics of re-entry\ncombining consideration of realistic effects with relative simplicity of\nresults .\n', 
  'has anyone formally determined the influence of joule heating,  produced\nby the induced current,  in magnetohydrodynamic free convection flows\nunder general conditions .\n', 
  // 'why does the compressibility transformation fail to correlate the high\nspeed data for helium and air .\n', 
  // 'did anyone else discover that the turbulent skin friction is not over\nsensitive to the nature of the variation of the viscosity with\ntemperature .\n', 
  // 'what progress has been made in research on unsteady aerodynamics .\n', 
  // 'what are the factors which influence the time required to invert large\nstructural matrices .\n', 
  // 'does a practical flow follow the theoretical concepts for the\ninteraction between adjacent blade rows of a supersonic cascade .\n', 
  // 'what is a single approximate formula for the displacement thickness of\na laminar boundary layer in compressible flow on a flat plate .\n', 
  // 'how is the design of ring or part ring wings by linear theory affected\nby thickness .\n', 
  // 'what application has the linear theory design of curved wings .\n', 
  // 'what is the effect of cross sectional shape on the flow over simple\ndelta wings with sharp leading edges .\n', 
  // 'papers on flow visualization on slender conical wings .\n', 
  // 'what size of end plate can be safely used to simulate two-dimensional\nflow conditions over a bluff cylindrical body of finite aspect ratio .\n', 
  // 'to find an approximate correction for thickness in slender thin-wing\ntheory .\n', 
  // 'how do interference-free longitudinal stability measurements (made\nusing free-flight models) compare with similar measurements made in\na low-blockage wind tunnel .\n', 
  // 'have wind tunnel interference effects been investigated on a systematic\nbasis .\n', 
  // 'are there any papers dealing with acoustic wave propagation in reacting\ngases .\n', 
  // 'has anyone investigated relaxation effects on gaseous heat transfer to a\nsuddenly heated wall .\n', 
  // 'are there any theoretical methods for predicting base pressure .\n', 
  // 'does transition in the hypersonic wake depend on body geometry and size\n', 
// ' 68\nhow can one detect transition phenomena in boundary layers .\n', ' 69\nhow can one detect transition phenomena in hypersonic wakes .\n', ' 71\nhas anyone investigated and developed a simple model for the vortex\nwake behind a cruciform wing .\n', ' 72\nwhat is a criterion that the transonic flow around an airfoil with a\nround leading edge be validly analyzed by the
// linearized transonic flow\ntheory .\n', ' 74\ncan the transonic flow around an arbitrary smooth thin airfoil be\nanalysed in a simple approximate way .\n', ' 79\nwhat are the details of the rigorous kinetic theory of gases .\n(chapman-enskog theory) .\n', ' 80\nhas anyone investigated the effect of surface mass transfer on\nhypersonic viscous interactions .\n', ' 81\nwhat is the combined effect of surface heat and mass transfer on\nhypersonic flow .\n', ' 82\nwhat are the existing
// solutions for hypersonic viscous interactions over\nan insulated flat plate .\n', ' 83\nwhat controls leading-edge attachment at transonic speeds .\n', ' 84\ncan
// the three-point boundary-value problem for the blasius equation\nbe integrated numerically,  using suitable transformations,  without\niteration on the boundary conditions .\n', ' 85\nwhat are the effects of small amounts of gas rarefaction on the\ncharacteristics of the boundary layers on slender bodies of revolution .\n', ' 86\nwhat is the available information pertaining to boundary layers on very\nslender bodies of revolution in continuum flow (the ?transverse\ncurvature  effect) .\n', ' 87\nwhat is the available information pertaining to the effect of slight\nrarefaction on boundary layer flows (the ?slip? effect) .\n', ' 93\nwhat investigations have been made of the flow field about a body moving\nthrough a rarefied,  partially ionized gas in the presence of a magnetic\nfield .\n', ' 94\nhow is the heat transfer downstream of the mass transfer region effected\nby mass transfer at the nose of a blunted cone .\n', ' 95\nto what extent can the available information for incompressible boundary\nlayers be applied to problems involving compressible boundary layers .\n', ' 97\nto what extent can readily available steady-state aerodynamic data be\nutilized to predict lifting-surface flutter characteristics .\n', ' 98\nwhat are the significant steady and non-steady flow characteristics\nwhich affect the flutter mechanism .\n', ' 99\nis it possible to determine rates of forced convective heat transfer\nfrom heated cylinders of non-circular cross-section,  (the fluid flow\nbeing along the generators) .\n', ' 100\nhow much is known about boundary layer flows along non-circular\ncylinders .\n', ' 101\nis there any simple,  but practical,  method for numerical integration\nof the
// mixing problem (i.e. the blasius problem with three-point\nboundary conditions) .\n', ' 102\ndoes there exist a closed-form expression for the local heat transfer\naround a yawed cylinder .\n', ' 103\nhow far around a cylinder and under what conditions of flow,  if any,\nis the velocity just outside of the boundary layer a linear function of\nthe distance around the cylinder .\n', ' 104\nwhere can i find pressure data on surfaces of swept cylinders .\n', " 105\ncan't the static deflection shapes be used in predicting flutter in\nplace of vibrational shapes . if so,  can we provide a justification by\nmeans of an example .\n", ' 106\ndoes the boundary layer on a flat plate in a shear flow induce a\npressure gradient .\n', ' 107\ncan the procedure of matching inner and outer solutions for a viscous\nflow problem be applied when the main stream is a shear flow .\n', ' 108\ncan series expansions be found for the boundary layer on a flat plate in\na shear flow .\n', ' 109\nwhat possible techniques are available for computing the injection\ndistribution corresponding to an isothermal transpiration cooled\nhemisphere .\n',
// ' 110\nwhat is known regarding asymptotic solutions to the exact boundary layer\nequations .\n', ' 111\nprevious solutions to the boundary layer similarity equations .\n', ' 112\nexperimental results on hypersonic viscous interaction .\n', ' 113\nwhat has been done about viscous interactions in relatively low reynolds\nnumber flows,  particularly at high mach numbers .\n', ' 114\nwhat role does the effect of chemical reaction (particularly when out of\nequilibrium) play in the similitude laws governing hypersonic flows over\nslender aerodynamic bodies .\n', ' 116\nhow significant is the possible pressure of a dissociated free stream\nwith respect to the realization of hypersonic simulation in high\nenthalpy wind tunnels .\n', ' 118\ndo the discrepancies among current analyses of the vorticity effect\non stagnation-point heat transfer result primarily from the\ndifferences in the viscosity-temperature law assumed .\n', ' 119\nhow far can one trust the linear
// viscosity-temperature solution\nassumed in some of the analyses of hypersonic shock layer at low\nreynolds number .\n', ' 120\nhow close is the comparison of the
// shock layer theory with existing\nexperiments in the low reynolds number (merged-layer) regime .\n', ' 121\nhas anyone explained the kink in the surge line of a multi-stage\naxial compressor .\n', ' 122\nhave any aerodynamic derivatives been measured at hypersonic mach\nnumbers and comparison been made with theoretical work .\n', ' 123\nare methods of measuring aerodynamic derivatives available which\ncould be adopted for use in short running time facilities .\n', ' 126\nwhat are wind-tunnel corrections for a two-dimensional aerofoil\nmounted off-centre in a tunnel .\n', " 128\nhow do kuchemann's and multhopp's methods for calculating lift\ndistributions on swept wings in subsonic flow compare with each other and with\nexperiment .\n", ' 130\nwhat is the present state of the theory of quasi-conical
// flows .\n', ' 131\nreferences on the methods available for accurately estimating\naerodynamic heat transfer to conical bodies for both laminar and turbulent\nflow .\n', ' 132\nwhat parameters can seriously influence natural transition\nfrom laminar to turbulent flow on a model in a wind tunnel .\n', ' 133\ncan a satisfactory experimental technique be developed for measuring\noscillatory derivatives on
// slender sting-mounted models in supersonic\nwind tunnels .\n', ' 135\nwhat effect has the boundary layer in modifying the basic inviscid flow\nbehind the shock,
// neglecting effects of leading edge and corner .\n', ' 136\nhow does a satellite orbit contract under the action of air drag in\nan atmosphere in which the scale height varies with altitude .\n', ' 137\nhow is the flow at transonic speeds about a delta wing different\nfrom that on a closely-related tapered sweptback wing .\n', ' 138\nrecent data on shock-induced boundary-layer separation .\n', ' 139\nwhat interference effects are likely at transonic speeds .\n', ' 140\ngiven complete freedom in the design of an airplane,  what procedure\nwould be used in order to minimize sonic boom intensity,  and is there a\nlimit to the degree of minimizing that can be accomplished .\n', ' 141\ncan methane-air combustion product be used as a hypersonic test\nmedium and predict, within experimental accuracies, the
// results\nobtained in air .\n', ' 142\nwhat is the theoretical heat transfer rate
// at the stagnation point of a\nblunt body .\n', ' 143\nwhat is the theoretical heat transfer distribution around a hemisphere .\n', ' 145\nhas anyone investigated
// the unsteady lift distributions on finite\nwings in subsonic flow .\n', ' 146\nwhat information is available for dynamic response of airplanes to\ngusts  or blasts in the subsonic regime .\n', ' 147\nwill forward or apex located controls be effective at low subsonic\nspeeds and how do they compare with conventional trailing-edge\nflaps .\n', ' 148\ngiven that an uncontrolled vehicle will tumble as it enters an\natmosphere, is it possible to predict when and how it will stop\ntumbling and its subsequent motion .\n', ' 149\nwhat are the effects of initial imperfections on the elastic buckling of\ncylindrical shells under axial compression .\n', ' 150\nwhy does the incremental theory and the deformation theory of plastic\nstress-strain relationship differ greatly when applied to stability\nproblems .\n', ' 152\nbasic dynamic characteristics of structures continuous over many spans
// .\n', ' 153\nis the information on the buckling of sandwich sphere available .\n', ' 154\ncan the load deformation characteristics of a beam be obtained with the\nmaterial being inelastic and a non uniform temperature being present .\n', ' 155\nwhat is the effect of an internal liquid column on the breathing\nvibrations of a cylindrical shell .\n', ' 156\nexperimental techniques in shell vibration .\n', ' 157\nin summarizing theoretical and experimental work on the behaviour of a\ntypical aircraft structure in a noise environment is it possible to\ndevelop a design procedure .\n', ' 158\nwhat data is there on the fatigue of structures under acoustic loading .\n', ' 160\npanels subjected to aerodynamic heating .\n', ' 161\ncan increasing the edge loading of a plate beyond the critical value for\nbuckling change the buckling mode .\n', ' 163\nhave the effects of an elastic edge restraint been considered in\nprevious papers on panel flutter .\n', ' 164\nhas the solution of the clamped plate problem,  in the classical theory\nof bending,  been reduced to two successive membrane boundary value\nproblems .\n', ' 165\nwhat
// data exists on oscillatory aerodynamic forces on control surfaces\nat transonic mach numbers .\n', ' 167\nit is not likely that the airforces on a wing of general planform\noscillating in transonic flow can be determined by purely analytical\nmethods . is it possible to determine the airforces on a single\nparticular planform, such as the rectangular one by such method .\n', ' 168\nis the problem of similarity for representative investigations of\naeroelastic effects in heated flow as intractable as previous investigations\nimply .\n', ' 169\nwhat is the magnitude and distribution of lift over the cone and the\ncylindrical portion of a cone-cylinder configuration .\n', ' 170\nis there any information on how the addition of a /boat-tail/ affects\nthe normal force on the body of various angles of incidence .\n', ' 171\nwhat are the aerodynamic interference effects on the fin lift
// and body\nlift of a fin-body combination .\n', ' 173\nwhat is the effect of initial axisymmetric deviations from circularity\non the non linear (large-deflection) load-deflection response of\ncylinders under hydrostatic pressure .\n', ' 175\nare previous analyses of circumferential thermal buckling of circular\ncylindrical shells unnecessarily involved or even inaccurate due to the\nassumed forms of buckling mode .\n', ' 176\nwhat papers are there dealing with circumferential buckling either\nthermal buckling or due to mechanical loading .\n', ' 177\nwhat analytical investigations have been made of the stability of\nconical shells . how do
// the results compare with experiment .\n', ' 181\nhas any work been done on determining the nature of compressible\nviscous flow in a straight channel .\n', ' 182\nin what areas, other than low density wind tunnel flows, is viscous\ncompressible flow in slender channels a problem .\nwhat analytical investigations have been
// made of the stability of\nconical shells . how do the results compare with experiment .\n', ' 183\njet interference with supersonic flow  -dash experimental papers .\n', ' 184\nthrust vector control by fluid injection -dash papers .\n', ' 187\nis it possible to obtain a reasonably simple analytical solution to the\nheat equation for an exponential (in time) heat input .\n', ' 189\nhas anyone programmed a pump design method for a high-speed digital\ncomputer .\n', ' 190\nhas anyone
// derived simplified pump design equation from the fundamental\nthree-dimensional equations for incompressible nonviscous flow .\n', ' 196\nwhat are the flutter characteristics of the exposed skin panels of the\nx-15 vertical stabilizer when subjected to aerodynamic heating .\n', ' 200\nwhat agreement is found between theoretically predicted instability\ntimes and experimentally measured collapse times for compressed columns\nin creep .\n', ' 201\ntheoretical studies of creep buckling .\n', ' 202\nexperimental studies of creep buckling .\n', ' 203\nis it possible to correlate the results on the creep buckling of widely\ndifferent structures within the framework of a single theory .\n', ' 204\nwhat are the experimental results for the creep buckling of columns .\n', ' 205\nwhat are the results for the
// creep buckling of round tubes under\nexternal pressure .\n', ' 206\nhave any analytical studies been conducted on the time-to-failure\nmechanism associated with creep collapse for a long circular cylindrical\nshell which exhibits both primary
// and secondary creep as well as elastic\ndeformations under various distributed force systems .\n', ' 208\nhas the effect of initial stresses,  on the frequencies
// of vibration of\ncircular cylindrical shells,  been investigated .\n', ' 209\nhas the effect of the change of initial pressure due to deformation,  on\nthe frequencies of vibration of circular cylindrical shells been\ninvestigated .\n', ' 210\nwhat are the discontinuity stresses at junctions in pressurized\nstructures .\n', ' 211\nwhat analytical solutions are available for stresses in edge-loaded\nshells of revolution .\n', ' 212\nwhat dome contours minimize discontinuity stresses when used as closures\non cylindrical pressure vessels .\n', ' 213\nwhat general solutions for the stresses in pressurized shells of\nrevolution are available .\n', ' 214\ncan studies of pure membrane cylinders having no wall bending stiffness\nbut maintaining their shape by virtue of internal pressure provide any\ninsight into the behaviour of pressurized cylinders with finite wall\nstiffness .\n', ' 215\nwhat are the best experimental data and classical small deflection\ntheory
// analyses available for pressurized cylinders in bending .\n', ' 216\ndoes a membrane theory exist by which the behaviour of pressurized\nmembrane cylinders in bending can be predicted .\n', ' 217\nwhat are the equations which define the stability of simply supported\ncorrugated core sandwich cylinders .\n', ' 218\npapers on small deflection theory for buckling of sandwich cylinders .\n', ' 219\nhas anyone developed an analysis which accurately establishes the large\ndeflection behaviour of conical shells .\n', ' 223\nwhat is the magnitude of second-order wing-body interference\nat high supersonic mach number .\n', ' 224\nwhat is the best theoretical method for calculating pressure on the\nsurface of a wing alone .\n', ' 225\nhow can the effect of the boundary-layer on wing pressure be calculated,\nand what is its magnitude .\n', ' 226\nhow should the navier-stokes difference equations be solved .\n', ' 227\nwhich  iterative method for solving linear elliptic\ndifference equations is most rapidly convergent .\n', ' 230\ntechnical report on measurement of ablation during flight .\n', ' 231\nwhat qualitative and quantitative material is available on ablation\nmaterials research .\n', ' 232\nhave flow fields been calculated for blunt-nosed bodies and compared\nwith experiment for a wide range of free stream conditions and body\nshapes .\n', ' 233\nwhat are the available properties of high-temperature air .\n', ' 234\nwhat is the magnitude of aerodynamic damping in flexible vibration modes\nof a slender body of revolution characteristic of launch vehicles .\n', ' 241\ncompressive circumferential stresses in a torispherical shell reveal\nthe possibility of buckling under internal pressure . has anyone\ninvestigated for which ranges of shell parameters these
// stresses are\nsufficiently large to cause elastic buckling .\n', ' 245\nis there
// an integral method to give a single and sufficiently accurate\nmethod of calculating the laminar separate point for various\nincompressible and compressible boundary layers with zero heat transfer .\n', ' 246\nwhat accurate or exact solutions
// of the laminar separation point for\nvarious incompressible and compressible boundary layers with zero heat\ntransfer are available .\n', ' 247\ncan the hypersonic similarity results be applied to the technique of\npredicting surface pressures of an ogive forebody at angle of attack .\n', ' 250\nwhat determines the onset of shock-induced boundary-layer separation .\n', ' 251\nare the stable profiles of a compressible boundary layer induced by a\nmoving wave known .\n', ' 252\nare there experimental results on the stability of a compressible\nboundary layer induced by a moving wave .\n', ' 253\nexact solution methods for calculating the ablative mass loss of a\nmaterial ablating at high temperatures in a hypersonic flight\nenvironment .\n', ' 254\nwhat approximate solutions are known to the direct problem of transonic\nflow in the throat of a nozzle,  i.e. finding the flow in a given\nnozzle .\n', ' 255\nwhat approximate solutions are known to the indirect problem of\ntransonic flow in the throat of a nozzle,  i.e. finding a nozzle which\nhas a given axial velocity distribution .\n', ' 257\nwhy do users of orthodox pitot-static tubes often find that the\ncalibrations appear to be,. - (a) significantly different from those formerly\nspecified,  (b) wildly variable at low reynolds numbers .\n', ' 259\nhas a comparison been made between interference-free drag measurements\nusing free-flight models and similar measurements made in a low-blockage\nwind tunnel .\n', ' 261\nsolution of the blasius problem with three-point boundary conditions .\n', " 264\nreferences on lyapunov's method on the stability of linear\ndifferential equations with periodic coefficients .\n", ' 265\nobtain all papers and reports that contain shock detachment distance\ndata .\n', ' 266\nwork on flow in channels at low reynolds numbers .\n', " 267\nsome approximate
// analytical heat conduction solutions using methods\nother than biot's principle .\n", ' 268\nwhat mode of stalling can be expected for each stage of an axial\ncompressor .\n', ' 269\nhas a criterion been established for determining the axial compressor\nchoking line .\n', ' 272\nhas a theory of quasi-conical flows been developed, in supersonic\nlinearised theory, for which the upwash distribution on the lifting\nsurface, apart from being a homogeneous function in the\nco-ordinate,
// is permitted to have a quite general functional form .\n', ' 273\nhow does scale
// height vary with altitude in an atmosphere .\n', ' 274\njet interference with supersonic flows\ntheoretical papers .\n', ' 275\neffects of leading-edge bluntness
// on the flutter characteristics of some\nsquare-planform double-wedge airfoils at
// mach numbers less than 15.4.\n', ' 277\nwhat factors have been shown to have a primary influence on sonic boom\nstrength .\n', ' 283\nwork on small-oscillation re-entry motions .\n', ' 284\nexperimental studies on panel flutter .\n', ' 285\nhow can wing-body,  flow field interference effects be approximated\nrationally .\n', ' 288\nhas anyone analytically or experimentally investigated the effects of\ninternal pressure on the buckling of circular-cylindrical shells under\nbending .\n', ' 291\nwhat theoretical and experimental work has been done on the excitation\nand response of typical structures in a noise environment .\n', ' 292\nis there a design method for calculating thermal fatigue endurances of\ncomponents of various types and sizes in a variety of circumstances .\n', ' 293\nwill an analysis of panel flutter based on arbitrarily assumed modes of\ndeformation prove satisfactory,  and if so,  what is the minimum number\nof modes that need be considered .\n', ' 294\nwhat is the criterion for true panel flutter,  as opposed to small\namplitude vibration arising from acoustic disturbances .\n', ' 295\npapers dealing with uniformly loaded sectors .\n', ' 296\ngeneral methods of solving clamped
// plate problems .\n', ' 297\nhow can the analytical solution of the buckling strength of a uniform\ncircular cylinder loaded in axial compression be refined so as
// to lower\nthe buckling load .\n', ' 298\nin the problem of the buckling strength
// of uniform circular cylinders\nloaded in axial compression,  does the linear solution help with\nimproving the non-linear one .\n', ' 299\nthe problem of similarity for representative investigation of\naeroelastic effects in a flow with the absence of heating effects .\n', ' 300\nhow is fatigue damage estimated using the normal long-hand method .\n', ' 301\nis there any information available on the difference in the effects of\nvarious edge conditions on the buckling of cylindrical shells .\n', ' 303\nhave non-linear large deflection analyses been conducted for shell\nshapes other than conical .\n', ' 304\nare asymptotic methods sufficiently accurate in the determination of\npre-buckling stresses in torispherical shells,  or must we resort to\nnumerical methods .\n', ' 306\nwhat are the nonequilibrium chemical constituents in the viscous shock\nlayer ahead of a blunt re-entry vehicle .\n', ' 314\nhow accurate are existing analytical theories in estimating pressure\ndistributions on cones at incidence,  at hypersonic speeds .\n', ' 315\nare simple empirical methods of any use for estimating pressure\ndistribution in cones .\n', ' 316\ndo viscous effects seriously modify pressure distributions .\n', ' 317\nhas anyone investigated theoretically whether surface flexibility\ncan stabilize a laminar boundary layer .\n', ' 321\nhow do subsonic and transonic flutter data measured in the new langley\ntransonic dynamics tunnel compare with similar data obtained in other\nfacilities .\n', ' 323\nhow do large changes in new mass ratio quantitatively affect\nwing-flutter boundaries .\n', ' 327\nwhat is the effect of the shape of the drag polar of a lifting\nspacecraft on the amount of
// reduction in maximum deceleration obtainable by\ncontinuously varying the aerodynamic coefficients during re-entry .\n', ' 331\nwhat are the physical significance and characteristics of separated\nlaminar and turbulent boundary layer flows .\n', ' 332\nhas anyone analytically investigated the stabilizing influence of soft\nelastic cores on the buckling strength of cylindrical shells subjected\nto non-uniform external pressure .\n', ' 333\nwhat papers are available on the buckling of empty cylindrical shells\nunder non-uniform pressure .\n', ' 335\nwhat effect do thermal stresses have on the compressive buckling\nstrength of ring-stiffened cylinders .\n', ' 336\nwhat is the effect on cylinder buckling of a circumferential stress\nsystem that varies in the axial direction .\n', ' 338\ncan non-linear shallow shell analysis be reduced to an engineering\ntechnique by use of the matrix .\n', ' 339\nis it possible to predict the shape of a shroud which will allow\nsimulation of the nose region flow field for a sphere in hypersonic flow .\n', '
// 340\nwhat investigations have been made of the wave system created by a\nstatic pressure distribution over a liquid surface .\n', ' 347\nhas anyone investigated the effect of shock generated vorticity on heat\ntransfer to a blunt body .\n', '
// 348\nwhat is the heat transfer to a blunt body in the absence of vorticity .\n',
// ' 349\nwhat are the general effects on flow fields when the reynolds number is\nsmall .\n', ' 352\nfind a calculation procedure applicable to all incompressible laminar\nboundary layer flow problems having good accuracy and reasonable\ncomputation time .\n', ' 353\npapers applicable to this problem (calculation procedures
// for laminar\nincompressible flow with arbitrary pressure gradient) .\n', ' 355\nhas anyone investigated the shear buckling of stiffened plates .\n', ' 356\npapers on shear buckling of unstiffened rectangular plates under shear .\n', ' 360\nin
// practice, how close to reality are the assumptions that the flow\nin a hypersonic shock tube using nitrogen is non-viscous and in\nthermodynamic equilibrium .\n', ' 365\nwhat design factors can be used to control lift-drag ratios at mach\nnumbers above 5 .\n'
]

const linksList = [
				 {
                id: 1,
                title: "007 GoldenEye Reloaded",
                content: "1st Person Shooter",
                img: "https://m.media-amazon.com/images/I/813kZphLwCL._AC_SY500_.jpg"
            },{
                id: 2,
                title: "2006 FIFA World Cup",
                content: "1st Person Shooter",
                img: "https://m.media-amazon.com/images/I/5195746QJKL.jpg"
            },{
                id: 3,
                title: "50 Cent Blood on the Sand",
                content: "1st Person Shooter",
                img: "https://m.media-amazon.com/images/I/813kZphLwCL._AC_SY500_.jpg"
            }, {
                id: 4,
                title: "Ace Combat Assault H",
                content: "1st Person Shooter",
                img: "https://archive.org/services/img/ace-combat-assault-horizon-xbox-360-english-singapore-region/full/pct:200/0/default.jpg"
            },{
                id: 5,
                title: "Ace Combat 6",
                content: "1st Person Shooter",
                img: "https://image.jeuxvideo.com/images-sm/x3/a/c/acc6x30f.jpg"
            },{
                id: 6,
                title: "Alan Wake",
                content: "1st Person Shooter",
                img: "https://www.mobygames.com/images/covers/l/186789-alan-wake-limited-collector-s-edition-xbox-360-front-cover.jpg"
            },
            {
                id: 7,
                title: "Alone In The Dark 4",
                content: "1st Person Shooter",
                img: "https://m.media-amazon.com/images/I/51ly8UrzkzL._SY445_.jpg"
            },
            {
                id: 8,
                title: "Angry Birds Star Wars",
                content: "1st Person Shooter",
                img: "https://m.media-amazon.com/images/I/91+wY37Cj8L._SL1500_.jpg"
            },
            {
                id: 9,
                title: "Apache Air Assault",
                content: "1st Person Shooter",
                img: "https://m.media-amazon.com/images/I/91ezXgZWeOL._SY445_.jpg"
            }]

            const stringOptions = [
  'Avocado', 
  'Banana', 
  'Cinammon', 
  'Dragon fruit', 
  'Eggs',
  'Farinha',
  'Goiaba',
  'Hummus',
  'Inha Benta',
  'Jiló'
]

export default defineComponent({
  name: "LoginPage",
  data() {
    return {
      bebidas: [],
      paginate: ["bebidas"],
      nombreCoctel: "",
      showPictures: ref(true),
      model: ref('Boolean'),
      query: ref('AAA'),
      dataBase: ref('Cranfield'),
      options: [
        'Boolean', 'Vector', 'Fuzzy'
      ],
      dataOptions: [
        'Cranfield', '20newspaper', 'Vaswani'
      ],
      queryOptions: default_queries,
      didSearch: false,
      posts : linksList,

            gamesList: [],
            page: 1,
            currentPage:1,
            nextPage: null,
            totalPages: 20,
            // q-select-input
            qoptions: stringOptions,
            tab: 'mails',
            popupOpen: false
    };
  },
  methods: {
    buscarCoctel() {
      var selectedDataBase = "cran";
      if (this.dataBase == "Vaswani"){
        selectedDataBase = "vas";
      }
      else if(this.dataBase == "Cranfield"){
        selectedDataBase = "cran";
      }else{
        selectedDataBase = "news";
      }
      var request = { 'query': this.nombreCoctel, 'data': selectedDataBase };
      const config = {
        'Content-Type': 'application/json',
        "Accept": "application/json",
      }
      //const result = await axios.post('https://testapi.org/post', { name: this.nombreCoctel });//this.nombreCoctel; //"/api/json/v1/1/search.php?s=" + this.nombreCoctel
      //var url = "https://jsonplaceholder.typicode.com/users";// + request;
      var url = "http://172.21.0.2:8000/"
      // if(this.model == 'Boolean'){
      //   url = url+"boolean/";
      // }
      // else if(this.model == "Vector"){
      //   url = url + "vect/";
      // }
      // else if(this.model == 'Fuzzy'){
      //   url = url+"fuzzy/"
      // }

      console.log("Checking env variable")
      console.log(process)
      console.log(process.env)
      console.log(process.env.MY_VARIABLE)
      axios.get(url, request={}, config ).then((res) => {
        this.gamesList = res.data;
        console.log(res);
        console.log(this.gamesList);
      }).catch(err => {
        // Handle error
        console.log("Error");
        console.log(err);
        //
        console.log("Request");
        console.log(res);
    });

      // axios.get("http://localhost:8000/api/boolean/").then((res) => {
      //   this.gamesList = res.data;
      //   // console.log(this.bebidas);
      // });
      // this.gamesList = [ {
      //           id: 1,
      //           title: "007 GoldenEye Reloaded",
      //           content: "1st Person Shooter",
      //           img: "https://m.media-amazon.com/images/I/813kZphLwCL._AC_SY500_.jpg"
      //       }];//this.posts.filter(x => x.title.toLowerCase().includes(this.nombreCoctel));
      console.log(this.gamesList);
      console.log(this.nombreCoctel); 
      // console.log(this.bebidas);
      this.didSearch = true;
    },
    // filterFn (val, update, abort) {
    //   update(() => {
    //     const needle = val.toLowerCase()
    //     this.options = stringOptions.filter(v => v.toLowerCase().indexOf(needle) > -1)
    //   })
    // },
    // onInputValue(val){
    //   this.model = val
    // },
    // onPopupShow(val){
    //   this.popupOpen = true 
    // },
    // onPopupHide(val){
    //   this.popupOpen = false 
    // },
    // onClick(event){
    //   //console.log()
    //   if (
    //     this.popupOpen === true 
    //     //&& event.target.nodeName.toLowerCase() === 'input' // only on click in input
    //   ) {
    //     event.stopImmediatePropagation()
    //   }
    //   // forces popup to show again. Can't avoid flickering
    //   //this.$refs.input.showPopup()
    // },
  },
  computed:{
		getData(){
			return 	this.gamesList.slice((this.page-1)*this.totalPages,(this.page-1)*this.totalPages+this.totalPages)
		}
	}
});
</script>

<style scoped>
/* img {
  height: 100%;
  width: 100%;
  object-fit: cover;
} */

 .img-background
  {
    /* position: absolute; */
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .search-btn{
    border: 2px solid #0099CC !important;
    border-radius: 6px !important;
    color: blue;
  }

  button{
    border: 2px solid #0099CC !important;
    border-radius: 6px !important;
    color: black;
    max-height: 50px;
  }
</style>