import fitz
import re
import pandas as pd
import numpy as np
from unidecode import unidecode

class Chunker:
    
    def __init__(self,):
        pass

    def __getPages(self,):
        block_dict = {}
        page_num = 1

        for page in self.file_obj:
            file_dict = page.get_text('dict')
            block = file_dict['blocks']
            block_dict[page_num] = block
            page_num += 1

        return block_dict
        
    def __extractText(self, block_dict):
        
        spans = pd.DataFrame(columns=['xmin', 'ymin', 'xmax', 'ymax', 'text', 'tag'])

        rows = []

        for pagenum, blocks in block_dict.items():
            for block in blocks:
                if block['type'] == 0:
                    for line in block['lines']:
                        for span in line['spans']:
                            xmin, ymin, xmax, ymax = list(span['bbox'])
                            font_size = span['size']
                            text = unidecode(span['text']).strip()
                            span_font = span['font']
                            is_upper = False
                            is_bold = False

                            if "bold" in span_font.lower():
                                is_bold = True

                            if re.sub("[\(\[].*?[\)\]]", "", text).isupper():
                                is_upper = True

                            if text.replace(" ","") !=  "":
                                rows.append((xmin, ymin, xmax, ymax, text, is_upper, is_bold, span_font, font_size, pagenum))

        span_df = pd.DataFrame(rows, columns=['xmin','ymin','xmax','ymax', 'text', 'is_upper','is_bold','span_font', 'font_size', 'page_num'])


        span_scores = []
        special = '[(_:/,#%\=@)]'

        for _, span_row in span_df.iterrows():
            score = round(span_row.font_size)
            text = span_row.text

            if not re.search(special, text):
                if span_row.is_bold:
                    score +=1

                if span_row.is_upper:
                    score +=1

            span_scores.append(score)

        values, counts = np.unique(span_scores, return_counts=True)

        values, counts = np.unique(span_scores, return_counts=True)
        style_dict = {}

        for value, count in zip(values, counts):
            style_dict[value] = count

        sorted(style_dict.items(), key=lambda x: x[1])

        p_size = max(style_dict, key=style_dict.get)
        idx = 0
        tag = {}

        for size in sorted(values, reverse = True):
            idx += 1

            if size == p_size:
                idx = 0
                tag[size] = 'p'

            if size > p_size:
                tag[size] = 'h{0}'.format(idx)

            if size < p_size:
                tag[size] = 's{0}'.format(idx)
        
        span_tags = [tag[score] for score in span_scores]
        span_df['tag'] = span_tags

        headings_list = []
        text_list = []
        tmp = []
        pg_list = []
        heading = ''
        pagenum_list = []

        for index, span_row in span_df.iterrows():
            text = span_row.text
            tag = span_row.tag
            page = span_row.page_num

            if 'h' in tag:
                headings_list.append(text)
                text_list.append('\n'.join(tmp))
                pagenum_list.append(sorted(list(set(pg_list))))
                tmp = []
                pg_list = []
                heading = text
            else:
                tmp.append(text)
                pg_list.append(page)

        text_list.append('\n'.join(tmp))
        text_list = text_list[1:]
        text_df = pd.DataFrame(zip(headings_list, text_list), columns=['Headers','Contents'])
        text_df['PageNo'] = pagenum_list
        return text_df
    
    def __merge_header_content(self, df):
        df = df.replace(np.nan, None)
        df['Headers'] = df['Headers'].replace("*", None)

        headerCon = ''
        contentCon = ''
        pageNumCon = list()
        finalPg = []
        data = []
        for index in range(len(df)):
            header = df.iloc[index]['Headers']
            content = df.iloc[index]['Contents']
            pageNum = df.iloc[index]['PageNo']
            # print(pageNum)
            
            if header:
                headerCon += " "+header.strip()
                headerCon = re.sub('[^a-zA-Z0-9  \'\.]', ' ', headerCon)
                headerCon = re.sub(' +', ' ', headerCon)
                
            if content:
                contentCon += " "+content.strip()
                contentCon = re.sub('[^a-zA-Z0-9 \'\.]', ' ', contentCon)
                contentCon = re.sub(' +', ' ', contentCon)
            
            if pageNum:
                pageNumCon.extend(pageNum)
                # print(pageNumCon)

            if header and content:
                # data[headerCon.strip()] = contentCon.strip()
                data.append([headerCon.strip(), contentCon.strip()])
                print("pageNumCon>>>>>>>>>>",pageNumCon)
                tmp = sorted(list(set(pageNumCon)))
                print("tmp>>>>>>>>>> ",tmp)
                tmp = ', '.join(str(x) for x in tmp)
                # finalPg.append(', '.join(str(x) for x in tmp))
                # print(type(tmp))
                finalPg.append(tmp)
                if len(data) != len(finalPg):
                    print("len(data) >>>>>>>>> ",str(len(data)))
                    print("len(finalPg) >>>>>>>>> ",str(len(finalPg)))
                    break
                
                headerCon = ''
                contentCon = ''
                pageNumCon = list()

        formatted_pd = pd.DataFrame(data, columns=['Headers','Contents'])
        formatted_pd['PageNo'] = finalPg
        
        return formatted_pd

    def run(self, file_path):
        self.file_obj = fitz.open(file_path)
        page_dict = self.__getPages()
        df = self.__extractText(page_dict)
        df = self.__merge_header_content(df)
        self.file_obj.close()
        return df

if __name__ == "__main__":
    filePath = "D:/Downloads/HR Policy Manual 2023 (8).pdf"
    chunk = Chunker()
    df = chunk.run(filePath)
    df.to_csv("D:/Downloads/HR Policy Manual 2023 (8)2.csv", index=False)
    pass
