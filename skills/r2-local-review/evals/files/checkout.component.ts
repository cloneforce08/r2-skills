import { Component, OnInit, Input, Output, EventEmitter, ChangeDetectorRef } from '@angular/core';
import { NgIf, NgFor, CurrencyPipe } from '@angular/common';
import { CartService } from '../services/cart.service';
import { OrderService } from '../services/order.service';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [NgIf, NgFor, CurrencyPipe],
  template: `
    <div *ngIf="items.length > 0">
      <ul>
        <li *ngFor="let item of items">
          {{ item.name }} x{{ item.quantity }} — {{ item.price * item.quantity | currency:'BRL' }}
        </li>
      </ul>
      <strong>Total: {{ total | currency:'BRL' }}</strong>
      <button (click)="placeOrder()" [disabled]="loading">Finalizar Pedido</button>
    </div>
    <div *ngIf="items.length === 0">Carrinho vazio</div>
  `
})
export class CheckoutComponent implements OnInit {
  @Input() userId!: string;
  @Output() orderPlaced = new EventEmitter<string>();

  items: CartItem[] = [];
  total = 0;
  loading = false;

  constructor(
    private cartService: CartService,
    private orderService: OrderService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.cartService.getCartItems(this.userId).subscribe(items => {
      this.items = items;
      this.calculateTotal();
    });
  }

  calculateTotal() {
    this.total = 0;
    for (let i = 0; i < this.items.length; i++) {
      this.total = this.total + (this.items[i].price * this.items[i].quantity);
    }
  }

  placeOrder() {
    this.loading = true;
    const payload = {
      userId: this.userId,
      items: this.items,
      total: this.total,
      timestamp: new Date()
    };
    this.orderService.createOrder(payload).subscribe(order => {
      this.orderPlaced.emit(order.id);
      this.loading = false;
      console.log('Order placed:', order);
    });
  }
}
