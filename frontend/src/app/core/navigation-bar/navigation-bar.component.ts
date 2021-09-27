import { Component, OnInit } from '@angular/core';
import { marker as TEXT } from '@biesbjerg/ngx-translate-extract-marker';

import { NavItem } from '~/app/core/navigation-bar/navigation-bar-item/navigation-bar-item.component';

@Component({
  selector: 'cb-navigation-bar',
  templateUrl: './navigation-bar.component.html',
  styleUrls: ['./navigation-bar.component.scss']
})
export class NavigationBarComponent implements OnInit {
  showSubmenu = false;
  navItems: NavItem[] = [
    {
      name: TEXT('Dashboard'),
      icon: 'mdi mdi-apps',
      route: '/dashboard'
    },
    {
      name: TEXT('Users'),
      icon: 'mdi mdi-account-multiple',
      route: '/users'
    },
    {
      name: TEXT('Hosts'),
      icon: 'mdi mdi-server-network',
      route: '/hosts'
    }
  ];

  /* Subitem example. Can be removed as soon as we
     have an actual sub-item ;)
     {
       name: 'Parent Item',
       icon: 'mdi:apps',
       children: [{
         name: 'Subitem1',
         icon: 'mdi:airplane',
         route: '/subitem1'
       },{
         name: 'Subitem2',
         icon: 'mdi:account',
          route: '/subitem2'
      }]
    }
   */

  constructor() {}

  ngOnInit(): void {}
}
