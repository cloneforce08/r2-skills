export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

export interface Discount {
  type: 'percentage' | 'fixed';
  value: number;
}

export class CartService {
  private items: CartItem[] = [];

  add(item: CartItem): void {
    const existing = this.items.find(i => i.id === item.id);
    if (existing) {
      existing.quantity += item.quantity;
    } else {
      this.items.push({ ...item });
    }
  }

  remove(itemId: string): void {
    this.items = this.items.filter(i => i.id !== itemId);
  }

  getItems(): CartItem[] {
    return [...this.items];
  }

  getTotal(discount?: Discount): number {
    const subtotal = this.items.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0,
    );

    if (!discount) return subtotal;

    if (discount.type === 'percentage') {
      return subtotal * (1 - discount.value / 100);
    }

    return Math.max(0, subtotal - discount.value);
  }

  clear(): void {
    this.items = [];
  }
}
