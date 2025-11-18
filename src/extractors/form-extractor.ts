/**
 * Form discovery and extraction
 */

import * as cheerio from 'cheerio';
import { FormInfo, FormInput, ExtractedLink, LinkType } from '../types';
import { UrlUtils } from '../utils/url-utils';

export class FormExtractor {
  /**
   * Extract all forms from HTML content
   */
  static extractForms(html: string, baseUrl: string): FormInfo[] {
    const forms: FormInfo[] = [];
    const $ = cheerio.load(html);

    $('form').each((_, formElem) => {
      const $form = $(formElem);

      // Get form action
      let action = $form.attr('action') || baseUrl;
      try {
        action = UrlUtils.resolve(baseUrl, action);
      } catch {
        action = baseUrl;
      }

      // Get form method
      const method = ($form.attr('method') || 'GET').toUpperCase();

      // Extract form inputs
      const inputs: FormInput[] = [];

      $form.find('input, select, textarea').each((_, inputElem) => {
        const $input = $(inputElem);
        const tagName = inputElem.name.toLowerCase();

        const input: FormInput = {
          name: $input.attr('name') || '',
          type: $input.attr('type') || tagName,
          value: $input.attr('value'),
          required: $input.attr('required') !== undefined,
          attributes: this.getAttributes(inputElem),
        };

        // Handle select options
        if (tagName === 'select') {
          const options: string[] = [];
          $input.find('option').each((_, optionElem) => {
            const value = $(optionElem).attr('value') || $(optionElem).text();
            options.push(value);
          });
          input.attributes = input.attributes || {};
          input.attributes.options = JSON.stringify(options);
        }

        inputs.push(input);
      });

      forms.push({
        action,
        method,
        inputs,
        attributes: this.getAttributes(formElem),
      });
    });

    return forms;
  }

  /**
   * Extract form action URLs as links
   */
  static extractFormLinks(html: string, baseUrl: string): ExtractedLink[] {
    const links: ExtractedLink[] = [];
    const forms = this.extractForms(html, baseUrl);

    for (const form of forms) {
      try {
        if (UrlUtils.isValidHttpUrl(form.action)) {
          links.push({
            url: form.action,
            normalizedUrl: UrlUtils.normalize(form.action),
            type: LinkType.FORM_ACTION,
            attributes: {
              method: form.method,
              inputCount: form.inputs.length.toString(),
            },
          });
        }
      } catch {
        // Skip invalid URLs
      }
    }

    return links;
  }

  /**
   * Get all attributes from an element
   */
  private static getAttributes(elem: any): Record<string, string> {
    const attributes: Record<string, string> = {};
    const attribs = elem.attribs || {};

    for (const [key, value] of Object.entries(attribs)) {
      attributes[key] = value as string;
    }

    return attributes;
  }
}
